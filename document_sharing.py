#!/usr/bin/env python3
"""
Service de partage de documents pour DocSearch AI
Gère le partage de documents entre utilisateurs avec permissions et expiration
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from models import Document, DocumentShare, User
from auth import get_current_user

logger = logging.getLogger(__name__)

class DocumentSharingService:
    """Service de gestion du partage de documents"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def share_document(self, document_id: int, owner_id: int, shared_with_email: str,
                      permissions: List[str] = None, expires_at: datetime = None,
                      message: str = None) -> DocumentShare:
        """
        Partage un document avec un autre utilisateur
        
        Args:
            document_id: ID du document à partager
            owner_id: ID du propriétaire du document
            shared_with_email: Email de l'utilisateur avec qui partager
            permissions: Liste des permissions (read, write, comment, share)
            expires_at: Date d'expiration du partage
            message: Message optionnel pour le partage
            
        Returns:
            DocumentShare créé
        """
        try:
            # Vérifier que le document appartient à l'utilisateur
            document = self.db.query(Document).filter(
                and_(Document.id == document_id, Document.user_id == owner_id)
            ).first()
            
            if not document:
                raise ValueError("Document non trouvé ou accès non autorisé")
            
            # Trouver l'utilisateur avec qui partager
            shared_with_user = self.db.query(User).filter(
                User.email == shared_with_email
            ).first()
            
            if not shared_with_user:
                raise ValueError(f"Utilisateur avec l'email {shared_with_email} non trouvé")
            
            if shared_with_user.id == owner_id:
                raise ValueError("Impossible de partager un document avec soi-même")
            
            # Vérifier si le partage existe déjà
            existing_share = self.db.query(DocumentShare).filter(
                and_(
                    DocumentShare.document_id == document_id,
                    DocumentShare.shared_with == shared_with_user.id,
                    DocumentShare.is_active == True
                )
            ).first()
            
            if existing_share:
                # Mettre à jour le partage existant
                if permissions:
                    existing_share.permissions = permissions
                if expires_at:
                    existing_share.expires_at = expires_at
                if message:
                    existing_share.message = message
                
                existing_share.updated_at = datetime.now()
                self.db.commit()
                self.db.refresh(existing_share)
                
                logger.info(f"Partage mis à jour pour le document {document_id}")
                return existing_share
            
            # Créer un nouveau partage
            default_permissions = permissions or ["read"]
            
            share = DocumentShare(
                document_id=document_id,
                shared_by=owner_id,
                shared_with=shared_with_user.id,
                permissions=default_permissions,
                expires_at=expires_at,
                message=message,
                created_at=datetime.now(),
                is_active=True
            )
            
            self.db.add(share)
            self.db.commit()
            self.db.refresh(share)
            
            logger.info(f"Document {document_id} partagé avec {shared_with_email}")
            return share
            
        except Exception as e:
            logger.error(f"Erreur lors du partage du document: {e}")
            self.db.rollback()
            raise
    
    def get_shared_documents(self, user_id: int, as_owner: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère les documents partagés avec un utilisateur ou par un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            as_owner: True pour récupérer les documents partagés par l'utilisateur,
                     False pour récupérer les documents partagés avec l'utilisateur
            
        Returns:
            Liste des documents partagés avec leurs informations
        """
        try:
            if as_owner:
                # Documents partagés par l'utilisateur
                shares = self.db.query(DocumentShare).filter(
                    and_(
                        DocumentShare.shared_by == user_id,
                        DocumentShare.is_active == True
                    )
                ).order_by(desc(DocumentShare.created_at)).all()
            else:
                # Documents partagés avec l'utilisateur
                shares = self.db.query(DocumentShare).filter(
                    and_(
                        DocumentShare.shared_with == user_id,
                        DocumentShare.is_active == True,
                        or_(
                            DocumentShare.expires_at.is_(None),
                            DocumentShare.expires_at > datetime.now()
                        )
                    )
                ).order_by(desc(DocumentShare.created_at)).all()
            
            shared_docs = []
            for share in shares:
                # Récupérer les informations du document
                document = self.db.query(Document).filter(Document.id == share.document_id).first()
                if not document:
                    continue
                
                # Récupérer les informations de l'utilisateur
                if as_owner:
                    user = self.db.query(User).filter(User.id == share.shared_with).first()
                    user_info = {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "full_name": user.full_name
                    } if user else None
                else:
                    user = self.db.query(User).filter(User.id == share.shared_by).first()
                    user_info = {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "full_name": user.full_name
                    } if user else None
                
                shared_docs.append({
                    "share_id": share.id,
                    "document": {
                        "id": document.id,
                        "filename": document.filename,
                        "file_type": document.file_type,
                        "file_size": document.file_size,
                        "upload_date": document.upload_date.isoformat() if document.upload_date else None
                    },
                    "user": user_info,
                    "permissions": share.permissions,
                    "expires_at": share.expires_at.isoformat() if share.expires_at else None,
                    "message": share.message,
                    "created_at": share.created_at.isoformat(),
                    "is_expired": share.expires_at and share.expires_at < datetime.now()
                })
            
            return shared_docs
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des documents partagés: {e}")
            raise
    
    def get_share(self, share_id: int, user_id: int) -> Optional[DocumentShare]:
        """
        Récupère un partage spécifique
        
        Args:
            share_id: ID du partage
            user_id: ID de l'utilisateur (pour vérification des permissions)
            
        Returns:
            DocumentShare ou None
        """
        try:
            share = self.db.query(DocumentShare).filter(
                DocumentShare.id == share_id
            ).first()
            
            if not share:
                return None
            
            # Vérifier que l'utilisateur a accès à ce partage
            if share.shared_by != user_id and share.shared_with != user_id:
                raise ValueError("Accès non autorisé à ce partage")
            
            return share
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du partage: {e}")
            raise
    
    def update_share_permissions(self, share_id: int, owner_id: int, 
                                permissions: List[str]) -> DocumentShare:
        """
        Met à jour les permissions d'un partage
        
        Args:
            share_id: ID du partage
            owner_id: ID du propriétaire du document
            permissions: Nouvelles permissions
            
        Returns:
            DocumentShare mis à jour
        """
        try:
            share = self.db.query(DocumentShare).filter(
                and_(
                    DocumentShare.id == share_id,
                    DocumentShare.shared_by == owner_id
                )
            ).first()
            
            if not share:
                raise ValueError("Partage non trouvé ou accès non autorisé")
            
            share.permissions = permissions
            share.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(share)
            
            logger.info(f"Permissions mises à jour pour le partage {share_id}")
            return share
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des permissions: {e}")
            self.db.rollback()
            raise
    
    def extend_share_expiration(self, share_id: int, owner_id: int, 
                               new_expires_at: datetime) -> DocumentShare:
        """
        Prolonge l'expiration d'un partage
        
        Args:
            share_id: ID du partage
            owner_id: ID du propriétaire du document
            new_expires_at: Nouvelle date d'expiration
            
        Returns:
            DocumentShare mis à jour
        """
        try:
            share = self.db.query(DocumentShare).filter(
                and_(
                    DocumentShare.id == share_id,
                    DocumentShare.shared_by == owner_id
                )
            ).first()
            
            if not share:
                raise ValueError("Partage non trouvé ou accès non autorisé")
            
            share.expires_at = new_expires_at
            share.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(share)
            
            logger.info(f"Expiration prolongée pour le partage {share_id}")
            return share
            
        except Exception as e:
            logger.error(f"Erreur lors de la prolongation de l'expiration: {e}")
            self.db.rollback()
            raise
    
    def revoke_share(self, share_id: int, owner_id: int) -> bool:
        """
        Révoque un partage
        
        Args:
            share_id: ID du partage
            owner_id: ID du propriétaire du document
            
        Returns:
            True si révoqué
        """
        try:
            share = self.db.query(DocumentShare).filter(
                and_(
                    DocumentShare.id == share_id,
                    DocumentShare.shared_by == owner_id
                )
            ).first()
            
            if not share:
                raise ValueError("Partage non trouvé ou accès non autorisé")
            
            share.is_active = False
            share.revoked_at = datetime.now()
            
            self.db.commit()
            
            logger.info(f"Partage {share_id} révoqué")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la révocation du partage: {e}")
            self.db.rollback()
            raise
    
    def check_permission(self, document_id: int, user_id: int, 
                        required_permission: str) -> bool:
        """
        Vérifie si un utilisateur a une permission spécifique sur un document
        
        Args:
            document_id: ID du document
            user_id: ID de l'utilisateur
            required_permission: Permission requise (read, write, comment, share)
            
        Returns:
            True si l'utilisateur a la permission
        """
        try:
            # Vérifier si l'utilisateur est le propriétaire
            document = self.db.query(Document).filter(
                and_(Document.id == document_id, Document.user_id == user_id)
            ).first()
            
            if document:
                return True  # Le propriétaire a toutes les permissions
            
            # Vérifier les partages actifs
            share = self.db.query(DocumentShare).filter(
                and_(
                    DocumentShare.document_id == document_id,
                    DocumentShare.shared_with == user_id,
                    DocumentShare.is_active == True,
                    or_(
                        DocumentShare.expires_at.is_(None),
                        DocumentShare.expires_at > datetime.now()
                    )
                )
            ).first()
            
            if share and required_permission in share.permissions:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des permissions: {e}")
            return False
    
    def get_share_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Récupère les statistiques des partages d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Statistiques des partages
        """
        try:
            # Partages créés par l'utilisateur
            shares_created = self.db.query(DocumentShare).filter(
                and_(
                    DocumentShare.shared_by == user_id,
                    DocumentShare.is_active == True
                )
            ).count()
            
            # Partages reçus par l'utilisateur
            shares_received = self.db.query(DocumentShare).filter(
                and_(
                    DocumentShare.shared_with == user_id,
                    DocumentShare.is_active == True,
                    or_(
                        DocumentShare.expires_at.is_(None),
                        DocumentShare.expires_at > datetime.now()
                    )
                )
            ).count()
            
            # Partages expirés
            expired_shares = self.db.query(DocumentShare).filter(
                and_(
                    DocumentShare.shared_by == user_id,
                    DocumentShare.is_active == True,
                    DocumentShare.expires_at < datetime.now()
                )
            ).count()
            
            # Documents les plus partagés
            most_shared_docs = self.db.query(
                Document.filename,
                func.count(DocumentShare.id)
            ).join(DocumentShare).filter(
                and_(
                    Document.user_id == user_id,
                    DocumentShare.is_active == True
                )
            ).group_by(Document.id, Document.filename).order_by(
                func.count(DocumentShare.id).desc()
            ).limit(5).all()
            
            return {
                "shares_created": shares_created,
                "shares_received": shares_received,
                "expired_shares": expired_shares,
                "most_shared_documents": [
                    {"filename": filename, "count": count} 
                    for filename, count in most_shared_docs
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            raise
    
    def cleanup_expired_shares(self) -> int:
        """
        Nettoie les partages expirés (marquage comme inactifs)
        
        Returns:
            Nombre de partages nettoyés
        """
        try:
            expired_shares = self.db.query(DocumentShare).filter(
                and_(
                    DocumentShare.is_active == True,
                    DocumentShare.expires_at < datetime.now()
                )
            ).all()
            
            cleaned_count = 0
            for share in expired_shares:
                share.is_active = False
                share.revoked_at = datetime.now()
                cleaned_count += 1
            
            self.db.commit()
            
            logger.info(f"{cleaned_count} partages expirés nettoyés")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des partages: {e}")
            self.db.rollback()
            raise 