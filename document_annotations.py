#!/usr/bin/env python3
"""
Service d'annotations et de tags pour DocSearch AI
Gère les annotations, commentaires et tags sur les documents
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from models import Document, DocumentAnnotation, DocumentTag, User
from auth import get_current_user

logger = logging.getLogger(__name__)

class DocumentAnnotationService:
    """Service de gestion des annotations et tags de documents"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_annotation(self, document_id: int, user_id: int, 
                         annotation_type: str, content: str, 
                         position: Dict[str, Any] = None, 
                         tags: List[str] = None) -> DocumentAnnotation:
        """
        Crée une nouvelle annotation sur un document
        
        Args:
            document_id: ID du document
            user_id: ID de l'utilisateur
            annotation_type: Type d'annotation (highlight, comment, note, etc.)
            content: Contenu de l'annotation
            position: Position dans le document (page, line, etc.)
            tags: Liste de tags associés
            
        Returns:
            DocumentAnnotation créée
        """
        try:
            # Vérifier que l'utilisateur a accès au document
            document = self.db.query(Document).filter(
                and_(Document.id == document_id, Document.user_id == user_id)
            ).first()
            
            if not document:
                raise ValueError("Document non trouvé ou accès non autorisé")
            
            # Créer l'annotation
            annotation = DocumentAnnotation(
                document_id=document_id,
                user_id=user_id,
                annotation_type=annotation_type,
                content=content,
                position=json.dumps(position) if position else None,
                tags=json.dumps(tags) if tags else [],
                created_at=datetime.now(),
                is_active=True
            )
            
            self.db.add(annotation)
            self.db.commit()
            self.db.refresh(annotation)
            
            logger.info(f"Nouvelle annotation créée pour le document {document_id}")
            return annotation
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'annotation: {e}")
            self.db.rollback()
            raise
    
    def get_document_annotations(self, document_id: int, user_id: int, 
                                annotation_type: str = None) -> List[DocumentAnnotation]:
        """
        Récupère toutes les annotations d'un document
        
        Args:
            document_id: ID du document
            user_id: ID de l'utilisateur
            annotation_type: Filtrer par type d'annotation (optionnel)
            
        Returns:
            Liste des annotations
        """
        try:
            # Vérifier les permissions
            document = self.db.query(Document).filter(
                and_(Document.id == document_id, Document.user_id == user_id)
            ).first()
            
            if not document:
                raise ValueError("Document non trouvé ou accès non autorisé")
            
            query = self.db.query(DocumentAnnotation).filter(
                and_(
                    DocumentAnnotation.document_id == document_id,
                    DocumentAnnotation.is_active == True
                )
            )
            
            if annotation_type:
                query = query.filter(DocumentAnnotation.annotation_type == annotation_type)
            
            annotations = query.order_by(desc(DocumentAnnotation.created_at)).all()
            
            return annotations
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des annotations: {e}")
            raise
    
    def get_annotation(self, annotation_id: int, user_id: int) -> Optional[DocumentAnnotation]:
        """
        Récupère une annotation spécifique
        
        Args:
            annotation_id: ID de l'annotation
            user_id: ID de l'utilisateur
            
        Returns:
            DocumentAnnotation ou None
        """
        try:
            annotation = self.db.query(DocumentAnnotation).filter(
                DocumentAnnotation.id == annotation_id
            ).first()
            
            if not annotation:
                return None
            
            # Vérifier les permissions
            document = self.db.query(Document).filter(
                and_(Document.id == annotation.document_id, Document.user_id == user_id)
            ).first()
            
            if not document:
                raise ValueError("Accès non autorisé à cette annotation")
            
            return annotation
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'annotation: {e}")
            raise
    
    def update_annotation(self, annotation_id: int, user_id: int, 
                         content: str = None, tags: List[str] = None) -> DocumentAnnotation:
        """
        Met à jour une annotation
        
        Args:
            annotation_id: ID de l'annotation
            user_id: ID de l'utilisateur
            content: Nouveau contenu (optionnel)
            tags: Nouveaux tags (optionnel)
            
        Returns:
            DocumentAnnotation mise à jour
        """
        try:
            annotation = self.get_annotation(annotation_id, user_id)
            if not annotation:
                raise ValueError("Annotation non trouvée ou accès non autorisé")
            
            if content is not None:
                annotation.content = content
            
            if tags is not None:
                annotation.tags = json.dumps(tags)
            
            annotation.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(annotation)
            
            logger.info(f"Annotation {annotation_id} mise à jour")
            return annotation
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'annotation: {e}")
            self.db.rollback()
            raise
    
    def delete_annotation(self, annotation_id: int, user_id: int) -> bool:
        """
        Supprime une annotation (marquage comme inactive)
        
        Args:
            annotation_id: ID de l'annotation
            user_id: ID de l'utilisateur
            
        Returns:
            True si supprimée
        """
        try:
            annotation = self.get_annotation(annotation_id, user_id)
            if not annotation:
                raise ValueError("Annotation non trouvée ou accès non autorisé")
            
            annotation.is_active = False
            annotation.deleted_at = datetime.now()
            
            self.db.commit()
            
            logger.info(f"Annotation {annotation_id} supprimée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'annotation: {e}")
            self.db.rollback()
            raise
    
    def search_annotations(self, user_id: int, query: str = None, 
                          annotation_type: str = None, tags: List[str] = None) -> List[DocumentAnnotation]:
        """
        Recherche dans les annotations
        
        Args:
            user_id: ID de l'utilisateur
            query: Texte à rechercher
            annotation_type: Filtrer par type
            tags: Filtrer par tags
            
        Returns:
            Liste des annotations correspondantes
        """
        try:
            # Construire la requête de base
            base_query = self.db.query(DocumentAnnotation).join(Document).filter(
                and_(
                    Document.user_id == user_id,
                    DocumentAnnotation.is_active == True
                )
            )
            
            # Ajouter les filtres
            if query:
                base_query = base_query.filter(
                    or_(
                        DocumentAnnotation.content.ilike(f"%{query}%"),
                        Document.filename.ilike(f"%{query}%")
                    )
                )
            
            if annotation_type:
                base_query = base_query.filter(DocumentAnnotation.annotation_type == annotation_type)
            
            if tags:
                for tag in tags:
                    base_query = base_query.filter(DocumentAnnotation.tags.contains(tag))
            
            annotations = base_query.order_by(desc(DocumentAnnotation.created_at)).all()
            
            return annotations
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'annotations: {e}")
            raise
    
    def get_annotation_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Récupère les statistiques des annotations d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Statistiques des annotations
        """
        try:
            # Total d'annotations
            total_annotations = self.db.query(DocumentAnnotation).join(Document).filter(
                and_(
                    Document.user_id == user_id,
                    DocumentAnnotation.is_active == True
                )
            ).count()
            
            # Par type d'annotation
            type_stats = self.db.query(
                DocumentAnnotation.annotation_type,
                func.count(DocumentAnnotation.id)
            ).join(Document).filter(
                and_(
                    Document.user_id == user_id,
                    DocumentAnnotation.is_active == True
                )
            ).group_by(DocumentAnnotation.annotation_type).all()
            
            # Documents les plus annotés
            document_stats = self.db.query(
                Document.filename,
                func.count(DocumentAnnotation.id)
            ).join(DocumentAnnotation).filter(
                and_(
                    Document.user_id == user_id,
                    DocumentAnnotation.is_active == True
                )
            ).group_by(Document.id, Document.filename).order_by(
                func.count(DocumentAnnotation.id).desc()
            ).limit(10).all()
            
            # Tags les plus utilisés
            all_tags = []
            annotations = self.db.query(DocumentAnnotation).join(Document).filter(
                and_(
                    Document.user_id == user_id,
                    DocumentAnnotation.is_active == True
                )
            ).all()
            
            for annotation in annotations:
                if annotation.tags:
                    try:
                        tags = json.loads(annotation.tags)
                        all_tags.extend(tags)
                    except:
                        pass
            
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_annotations": total_annotations,
                "annotations_by_type": dict(type_stats),
                "most_annotated_documents": [
                    {"filename": filename, "count": count} 
                    for filename, count in document_stats
                ],
                "top_tags": [
                    {"tag": tag, "count": count} 
                    for tag, count in top_tags
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            raise

class DocumentTagService:
    """Service de gestion des tags de documents"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tag(self, name: str, color: str = "#3B82F6", description: str = None) -> DocumentTag:
        """
        Crée un nouveau tag
        
        Args:
            name: Nom du tag
            color: Couleur du tag (hex)
            description: Description du tag
            
        Returns:
            DocumentTag créé
        """
        try:
            # Vérifier si le tag existe déjà
            existing_tag = self.db.query(DocumentTag).filter(
                DocumentTag.name == name
            ).first()
            
            if existing_tag:
                return existing_tag
            
            tag = DocumentTag(
                name=name,
                color=color,
                description=description,
                created_at=datetime.now(),
                is_active=True
            )
            
            self.db.add(tag)
            self.db.commit()
            self.db.refresh(tag)
            
            logger.info(f"Nouveau tag créé: {name}")
            return tag
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du tag: {e}")
            self.db.rollback()
            raise
    
    def get_all_tags(self) -> List[DocumentTag]:
        """Récupère tous les tags actifs"""
        try:
            return self.db.query(DocumentTag).filter(
                DocumentTag.is_active == True
            ).order_by(DocumentTag.name).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tags: {e}")
            raise
    
    def get_tag(self, tag_id: int) -> Optional[DocumentTag]:
        """Récupère un tag spécifique"""
        try:
            return self.db.query(DocumentTag).filter(
                DocumentTag.id == tag_id
            ).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du tag: {e}")
            raise
    
    def update_tag(self, tag_id: int, name: str = None, color: str = None, 
                   description: str = None) -> DocumentTag:
        """
        Met à jour un tag
        
        Args:
            tag_id: ID du tag
            name: Nouveau nom (optionnel)
            color: Nouvelle couleur (optionnel)
            description: Nouvelle description (optionnel)
            
        Returns:
            DocumentTag mis à jour
        """
        try:
            tag = self.get_tag(tag_id)
            if not tag:
                raise ValueError("Tag non trouvé")
            
            if name is not None:
                tag.name = name
            if color is not None:
                tag.color = color
            if description is not None:
                tag.description = description
            
            tag.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(tag)
            
            logger.info(f"Tag {tag_id} mis à jour")
            return tag
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du tag: {e}")
            self.db.rollback()
            raise
    
    def delete_tag(self, tag_id: int) -> bool:
        """
        Supprime un tag (marquage comme inactive)
        
        Args:
            tag_id: ID du tag
            
        Returns:
            True si supprimé
        """
        try:
            tag = self.get_tag(tag_id)
            if not tag:
                raise ValueError("Tag non trouvé")
            
            tag.is_active = False
            tag.deleted_at = datetime.now()
            
            self.db.commit()
            
            logger.info(f"Tag {tag_id} supprimé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du tag: {e}")
            self.db.rollback()
            raise
    
    def search_tags(self, query: str) -> List[DocumentTag]:
        """
        Recherche des tags par nom
        
        Args:
            query: Texte à rechercher
            
        Returns:
            Liste des tags correspondants
        """
        try:
            return self.db.query(DocumentTag).filter(
                and_(
                    DocumentTag.name.ilike(f"%{query}%"),
                    DocumentTag.is_active == True
                )
            ).order_by(DocumentTag.name).all()
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de tags: {e}")
            raise
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques des tags
        
        Returns:
            Statistiques des tags
        """
        try:
            # Total de tags
            total_tags = self.db.query(DocumentTag).filter(
                DocumentTag.is_active == True
            ).count()
            
            # Tags les plus utilisés
            tag_usage = {}
            annotations = self.db.query(DocumentAnnotation).filter(
                DocumentAnnotation.is_active == True
            ).all()
            
            for annotation in annotations:
                if annotation.tags:
                    try:
                        tags = json.loads(annotation.tags)
                        for tag in tags:
                            tag_usage[tag] = tag_usage.get(tag, 0) + 1
                    except:
                        pass
            
            top_tags = sorted(tag_usage.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_tags": total_tags,
                "most_used_tags": [
                    {"tag": tag, "count": count} 
                    for tag, count in top_tags
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques des tags: {e}")
            raise 