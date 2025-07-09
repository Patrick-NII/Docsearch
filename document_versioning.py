#!/usr/bin/env python3
"""
Service de versioning des documents pour DocSearch AI
Gère l'historique des versions, la comparaison et la restauration
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from models import Document, DocumentVersion, User
from auth import get_current_user

logger = logging.getLogger(__name__)

class DocumentVersioningService:
    """Service de gestion des versions de documents"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calcule le hash du contenu pour détecter les changements"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _extract_metadata(self, document: Document) -> Dict[str, Any]:
        """Extrait les métadonnées importantes du document"""
        return {
            "filename": document.filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "upload_date": document.upload_date.isoformat() if document.upload_date else None,
            "processing_status": document.processing_status,
            "session_id": document.session_id,
            "user_id": document.user_id
        }
    
    def create_version(self, document: Document, content: str, version_notes: str = None) -> DocumentVersion:
        """
        Crée une nouvelle version d'un document
        
        Args:
            document: Document source
            content: Contenu du document
            version_notes: Notes sur cette version
            
        Returns:
            DocumentVersion créée
        """
        try:
            # Calculer le hash du contenu
            content_hash = self._calculate_content_hash(content)
            
            # Vérifier si le contenu a changé
            latest_version = self.get_latest_version(document.id)
            if latest_version and latest_version.content_hash == content_hash:
                logger.info(f"Contenu identique pour le document {document.id}, pas de nouvelle version créée")
                return latest_version
            
            # Créer la nouvelle version
            version_number = self.get_next_version_number(document.id)
            
            new_version = DocumentVersion(
                document_id=document.id,
                version_number=version_number,
                content=content,
                content_hash=content_hash,
                metadata=json.dumps(self._extract_metadata(document)),
                version_notes=version_notes or f"Version {version_number} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                created_at=datetime.now(),
                created_by=document.user_id
            )
            
            self.db.add(new_version)
            self.db.commit()
            self.db.refresh(new_version)
            
            logger.info(f"Nouvelle version {version_number} créée pour le document {document.id}")
            return new_version
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la version: {e}")
            self.db.rollback()
            raise
    
    def get_versions(self, document_id: int, user_id: int) -> List[DocumentVersion]:
        """
        Récupère toutes les versions d'un document
        
        Args:
            document_id: ID du document
            user_id: ID de l'utilisateur (pour vérification des permissions)
            
        Returns:
            Liste des versions triées par numéro décroissant
        """
        try:
            # Vérifier que l'utilisateur a accès au document
            document = self.db.query(Document).filter(
                and_(Document.id == document_id, Document.user_id == user_id)
            ).first()
            
            if not document:
                raise ValueError("Document non trouvé ou accès non autorisé")
            
            versions = self.db.query(DocumentVersion).filter(
                DocumentVersion.document_id == document_id
            ).order_by(desc(DocumentVersion.version_number)).all()
            
            return versions
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des versions: {e}")
            raise
    
    def get_latest_version(self, document_id: int) -> Optional[DocumentVersion]:
        """Récupère la version la plus récente d'un document"""
        try:
            return self.db.query(DocumentVersion).filter(
                DocumentVersion.document_id == document_id
            ).order_by(desc(DocumentVersion.version_number)).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la dernière version: {e}")
            return None
    
    def get_version(self, version_id: int, user_id: int) -> Optional[DocumentVersion]:
        """
        Récupère une version spécifique
        
        Args:
            version_id: ID de la version
            user_id: ID de l'utilisateur (pour vérification des permissions)
            
        Returns:
            DocumentVersion ou None
        """
        try:
            version = self.db.query(DocumentVersion).filter(
                DocumentVersion.id == version_id
            ).first()
            
            if not version:
                return None
            
            # Vérifier les permissions
            document = self.db.query(Document).filter(
                and_(Document.id == version.document_id, Document.user_id == user_id)
            ).first()
            
            if not document:
                raise ValueError("Accès non autorisé à cette version")
            
            return version
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la version: {e}")
            raise
    
    def get_next_version_number(self, document_id: int) -> int:
        """Calcule le prochain numéro de version"""
        latest = self.get_latest_version(document_id)
        return (latest.version_number + 1) if latest else 1
    
    def compare_versions(self, version1_id: int, version2_id: int, user_id: int) -> Dict[str, Any]:
        """
        Compare deux versions d'un document
        
        Args:
            version1_id: ID de la première version
            version2_id: ID de la deuxième version
            user_id: ID de l'utilisateur
            
        Returns:
            Dictionnaire avec les différences
        """
        try:
            version1 = self.get_version(version1_id, user_id)
            version2 = self.get_version(version2_id, user_id)
            
            if not version1 or not version2:
                raise ValueError("Une ou les deux versions non trouvées")
            
            if version1.document_id != version2.document_id:
                raise ValueError("Les versions doivent appartenir au même document")
            
            # Comparaison simple basée sur le contenu
            content1 = version1.content
            content2 = version2.content
            
            # Calculer les différences
            lines1 = content1.split('\n')
            lines2 = content2.split('\n')
            
            added_lines = []
            removed_lines = []
            unchanged_lines = []
            
            # Comparaison ligne par ligne (simplifiée)
            for i, line in enumerate(lines1):
                if i < len(lines2):
                    if line == lines2[i]:
                        unchanged_lines.append(line)
                    else:
                        removed_lines.append(line)
                        added_lines.append(lines2[i])
                else:
                    removed_lines.append(line)
            
            # Ajouter les lignes supplémentaires de la version 2
            for i in range(len(lines1), len(lines2)):
                added_lines.append(lines2[i])
            
            return {
                "version1": {
                    "id": version1.id,
                    "version_number": version1.version_number,
                    "created_at": version1.created_at.isoformat(),
                    "notes": version1.version_notes
                },
                "version2": {
                    "id": version2.id,
                    "version_number": version2.version_number,
                    "created_at": version2.created_at.isoformat(),
                    "notes": version2.version_notes
                },
                "comparison": {
                    "total_lines_v1": len(lines1),
                    "total_lines_v2": len(lines2),
                    "unchanged_lines": len(unchanged_lines),
                    "added_lines": len(added_lines),
                    "removed_lines": len(removed_lines),
                    "added_content": added_lines,
                    "removed_content": removed_lines,
                    "similarity_percentage": len(unchanged_lines) / max(len(lines1), len(lines2)) * 100 if max(len(lines1), len(lines2)) > 0 else 100
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la comparaison des versions: {e}")
            raise
    
    def restore_version(self, version_id: int, user_id: int) -> DocumentVersion:
        """
        Restaure une version précédente en créant une nouvelle version
        
        Args:
            version_id: ID de la version à restaurer
            user_id: ID de l'utilisateur
            
        Returns:
            Nouvelle version créée avec le contenu restauré
        """
        try:
            version_to_restore = self.get_version(version_id, user_id)
            if not version_to_restore:
                raise ValueError("Version non trouvée ou accès non autorisé")
            
            # Récupérer le document
            document = self.db.query(Document).filter(Document.id == version_to_restore.document_id).first()
            if not document:
                raise ValueError("Document non trouvé")
            
            # Créer une nouvelle version avec le contenu restauré
            new_version = self.create_version(
                document=document,
                content=version_to_restore.content,
                version_notes=f"Restauration de la version {version_to_restore.version_number} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            logger.info(f"Version {version_to_restore.version_number} restaurée pour le document {document.id}")
            return new_version
            
        except Exception as e:
            logger.error(f"Erreur lors de la restauration de la version: {e}")
            raise
    
    def delete_version(self, version_id: int, user_id: int) -> bool:
        """
        Supprime une version (seulement si ce n'est pas la dernière)
        
        Args:
            version_id: ID de la version à supprimer
            user_id: ID de l'utilisateur
            
        Returns:
            True si supprimée, False sinon
        """
        try:
            version = self.get_version(version_id, user_id)
            if not version:
                raise ValueError("Version non trouvée ou accès non autorisé")
            
            # Vérifier que ce n'est pas la dernière version
            latest_version = self.get_latest_version(version.document_id)
            if latest_version and latest_version.id == version_id:
                raise ValueError("Impossible de supprimer la dernière version")
            
            self.db.delete(version)
            self.db.commit()
            
            logger.info(f"Version {version.version_number} supprimée pour le document {version.document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la version: {e}")
            self.db.rollback()
            raise
    
    def get_version_statistics(self, document_id: int, user_id: int) -> Dict[str, Any]:
        """
        Récupère les statistiques des versions d'un document
        
        Args:
            document_id: ID du document
            user_id: ID de l'utilisateur
            
        Returns:
            Statistiques des versions
        """
        try:
            versions = self.get_versions(document_id, user_id)
            
            if not versions:
                return {
                    "total_versions": 0,
                    "latest_version": None,
                    "first_version": None,
                    "version_history": []
                }
            
            return {
                "total_versions": len(versions),
                "latest_version": {
                    "number": versions[0].version_number,
                    "created_at": versions[0].created_at.isoformat(),
                    "notes": versions[0].version_notes
                },
                "first_version": {
                    "number": versions[-1].version_number,
                    "created_at": versions[-1].created_at.isoformat(),
                    "notes": versions[-1].version_notes
                },
                "version_history": [
                    {
                        "id": v.id,
                        "version_number": v.version_number,
                        "created_at": v.created_at.isoformat(),
                        "notes": v.version_notes,
                        "content_length": len(v.content)
                    }
                    for v in versions
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            raise 