#!/usr/bin/env python3
"""
Routes FastAPI pour la gestion avancée des documents
Inclut le versioning, les annotations, les tags et le partage
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from models import SessionLocal
from auth import get_current_user
from document_versioning import DocumentVersioningService
from document_annotations import DocumentAnnotationService, DocumentTagService
from document_sharing import DocumentSharingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents/advanced", tags=["Advanced Document Management"])

# Dependency pour obtenir la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# ROUTES DE VERSIONING
# ============================================================================

@router.get("/{document_id}/versions")
async def get_document_versions(
    document_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère toutes les versions d'un document"""
    try:
        versioning_service = DocumentVersioningService(db)
        versions = versioning_service.get_versions(document_id, current_user.id)
        
        return {
            "success": True,
            "document_id": document_id,
            "versions": [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "content_length": len(v.content),
                    "content_hash": v.content_hash,
                    "version_notes": v.version_notes,
                    "created_at": v.created_at.isoformat(),
                    "created_by": v.created_by
                }
                for v in versions
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des versions: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/versions/{version_id}")
async def get_version(
    version_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère une version spécifique"""
    try:
        versioning_service = DocumentVersioningService(db)
        version = versioning_service.get_version(version_id, current_user.id)
        
        if not version:
            raise HTTPException(status_code=404, detail="Version non trouvée")
        
        return {
            "success": True,
            "version": {
                "id": version.id,
                "document_id": version.document_id,
                "version_number": version.version_number,
                "content": version.content,
                "content_hash": version.content_hash,
                "version_notes": version.version_notes,
                "metadata": version.metadata,
                "created_at": version.created_at.isoformat(),
                "created_by": version.created_by
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la version: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/versions/compare")
async def compare_versions(
    version1_id: int,
    version2_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare deux versions d'un document"""
    try:
        versioning_service = DocumentVersioningService(db)
        comparison = versioning_service.compare_versions(version1_id, version2_id, current_user.id)
        
        return {
            "success": True,
            "comparison": comparison
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la comparaison: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/versions/{version_id}/restore")
async def restore_version(
    version_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restaure une version précédente"""
    try:
        versioning_service = DocumentVersioningService(db)
        new_version = versioning_service.restore_version(version_id, current_user.id)
        
        return {
            "success": True,
            "message": f"Version {new_version.version_number} créée avec le contenu restauré",
            "new_version": {
                "id": new_version.id,
                "version_number": new_version.version_number,
                "created_at": new_version.created_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la restauration: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/versions/{version_id}")
async def delete_version(
    version_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime une version (seulement si ce n'est pas la dernière)"""
    try:
        versioning_service = DocumentVersioningService(db)
        success = versioning_service.delete_version(version_id, current_user.id)
        
        return {
            "success": True,
            "message": "Version supprimée avec succès"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/{document_id}/versions/statistics")
async def get_version_statistics(
    document_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les statistiques des versions d'un document"""
    try:
        versioning_service = DocumentVersioningService(db)
        stats = versioning_service.get_version_statistics(document_id, current_user.id)
        
        return {
            "success": True,
            "statistics": stats
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# ============================================================================
# ROUTES D'ANNOTATIONS
# ============================================================================

@router.post("/{document_id}/annotations")
async def create_annotation(
    document_id: int,
    annotation_type: str,
    content: str,
    position: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée une nouvelle annotation sur un document"""
    try:
        annotation_service = DocumentAnnotationService(db)
        annotation = annotation_service.create_annotation(
            document_id=document_id,
            user_id=current_user.id,
            annotation_type=annotation_type,
            content=content,
            position=position,
            tags=tags
        )
        
        return {
            "success": True,
            "annotation": {
                "id": annotation.id,
                "document_id": annotation.document_id,
                "annotation_type": annotation.annotation_type,
                "content": annotation.content,
                "position": annotation.position,
                "tags": annotation.tags,
                "created_at": annotation.created_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'annotation: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/{document_id}/annotations")
async def get_document_annotations(
    document_id: int,
    annotation_type: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère toutes les annotations d'un document"""
    try:
        annotation_service = DocumentAnnotationService(db)
        annotations = annotation_service.get_document_annotations(
            document_id, current_user.id, annotation_type
        )
        
        return {
            "success": True,
            "annotations": [
                {
                    "id": a.id,
                    "annotation_type": a.annotation_type,
                    "content": a.content,
                    "position": a.position,
                    "tags": a.tags,
                    "created_at": a.created_at.isoformat(),
                    "updated_at": a.updated_at.isoformat() if a.updated_at else None
                }
                for a in annotations
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des annotations: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/annotations/{annotation_id}")
async def get_annotation(
    annotation_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère une annotation spécifique"""
    try:
        annotation_service = DocumentAnnotationService(db)
        annotation = annotation_service.get_annotation(annotation_id, current_user.id)
        
        if not annotation:
            raise HTTPException(status_code=404, detail="Annotation non trouvée")
        
        return {
            "success": True,
            "annotation": {
                "id": annotation.id,
                "document_id": annotation.document_id,
                "annotation_type": annotation.annotation_type,
                "content": annotation.content,
                "position": annotation.position,
                "tags": annotation.tags,
                "created_at": annotation.created_at.isoformat(),
                "updated_at": annotation.updated_at.isoformat() if annotation.updated_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'annotation: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/annotations/{annotation_id}")
async def update_annotation(
    annotation_id: int,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour une annotation"""
    try:
        annotation_service = DocumentAnnotationService(db)
        annotation = annotation_service.update_annotation(
            annotation_id, current_user.id, content, tags
        )
        
        return {
            "success": True,
            "annotation": {
                "id": annotation.id,
                "content": annotation.content,
                "tags": annotation.tags,
                "updated_at": annotation.updated_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/annotations/{annotation_id}")
async def delete_annotation(
    annotation_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime une annotation"""
    try:
        annotation_service = DocumentAnnotationService(db)
        success = annotation_service.delete_annotation(annotation_id, current_user.id)
        
        return {
            "success": True,
            "message": "Annotation supprimée avec succès"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/annotations/search")
async def search_annotations(
    query: Optional[str] = None,
    annotation_type: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recherche dans les annotations"""
    try:
        annotation_service = DocumentAnnotationService(db)
        annotations = annotation_service.search_annotations(
            current_user.id, query, annotation_type, tags
        )
        
        return {
            "success": True,
            "annotations": [
                {
                    "id": a.id,
                    "document_id": a.document_id,
                    "annotation_type": a.annotation_type,
                    "content": a.content,
                    "tags": a.tags,
                    "created_at": a.created_at.isoformat()
                }
                for a in annotations
            ]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/annotations/statistics")
async def get_annotation_statistics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les statistiques des annotations"""
    try:
        annotation_service = DocumentAnnotationService(db)
        stats = annotation_service.get_annotation_statistics(current_user.id)
        
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# ============================================================================
# ROUTES DE TAGS
# ============================================================================

@router.post("/tags")
async def create_tag(
    name: str,
    color: str = "#3B82F6",
    description: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un nouveau tag"""
    try:
        tag_service = DocumentTagService(db)
        tag = tag_service.create_tag(name, color, description)
        
        return {
            "success": True,
            "tag": {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "description": tag.description,
                "created_at": tag.created_at.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Erreur lors de la création du tag: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/tags")
async def get_all_tags(
    db: Session = Depends(get_db)
):
    """Récupère tous les tags"""
    try:
        tag_service = DocumentTagService(db)
        tags = tag_service.get_all_tags()
        
        return {
            "success": True,
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color,
                    "description": tag.description
                }
                for tag in tags
            ]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tags: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/tags/{tag_id}")
async def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """Récupère un tag spécifique"""
    try:
        tag_service = DocumentTagService(db)
        tag = tag_service.get_tag(tag_id)
        
        if not tag:
            raise HTTPException(status_code=404, detail="Tag non trouvé")
        
        return {
            "success": True,
            "tag": {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "description": tag.description
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du tag: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/tags/{tag_id}")
async def update_tag(
    tag_id: int,
    name: Optional[str] = None,
    color: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Met à jour un tag"""
    try:
        tag_service = DocumentTagService(db)
        tag = tag_service.update_tag(tag_id, name, color, description)
        
        return {
            "success": True,
            "tag": {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "description": tag.description,
                "updated_at": tag.updated_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/tags/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """Supprime un tag"""
    try:
        tag_service = DocumentTagService(db)
        success = tag_service.delete_tag(tag_id)
        
        return {
            "success": True,
            "message": "Tag supprimé avec succès"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/tags/search")
async def search_tags(
    query: str,
    db: Session = Depends(get_db)
):
    """Recherche des tags"""
    try:
        tag_service = DocumentTagService(db)
        tags = tag_service.search_tags(query)
        
        return {
            "success": True,
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color,
                    "description": tag.description
                }
                for tag in tags
            ]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/tags/statistics")
async def get_tag_statistics(
    db: Session = Depends(get_db)
):
    """Récupère les statistiques des tags"""
    try:
        tag_service = DocumentTagService(db)
        stats = tag_service.get_tag_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# ============================================================================
# ROUTES DE PARTAGE
# ============================================================================

@router.post("/{document_id}/share")
async def share_document(
    document_id: int,
    shared_with_email: str,
    permissions: List[str] = ["read"],
    expires_at: Optional[datetime] = None,
    message: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Partage un document avec un autre utilisateur"""
    try:
        sharing_service = DocumentSharingService(db)
        share = sharing_service.share_document(
            document_id=document_id,
            owner_id=current_user.id,
            shared_with_email=shared_with_email,
            permissions=permissions,
            expires_at=expires_at,
            message=message
        )
        
        return {
            "success": True,
            "message": f"Document partagé avec {shared_with_email}",
            "share": {
                "id": share.id,
                "document_id": share.document_id,
                "shared_with": share.shared_with,
                "permissions": share.permissions,
                "expires_at": share.expires_at.isoformat() if share.expires_at else None,
                "message": share.message,
                "created_at": share.created_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors du partage: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/shared")
async def get_shared_documents(
    as_owner: bool = False,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les documents partagés"""
    try:
        sharing_service = DocumentSharingService(db)
        shared_docs = sharing_service.get_shared_documents(current_user.id, as_owner)
        
        return {
            "success": True,
            "shared_documents": shared_docs
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des partages: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/shares/{share_id}")
async def get_share(
    share_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère un partage spécifique"""
    try:
        sharing_service = DocumentSharingService(db)
        share = sharing_service.get_share(share_id, current_user.id)
        
        if not share:
            raise HTTPException(status_code=404, detail="Partage non trouvé")
        
        return {
            "success": True,
            "share": {
                "id": share.id,
                "document_id": share.document_id,
                "shared_by": share.shared_by,
                "shared_with": share.shared_with,
                "permissions": share.permissions,
                "expires_at": share.expires_at.isoformat() if share.expires_at else None,
                "message": share.message,
                "created_at": share.created_at.isoformat(),
                "is_active": share.is_active
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du partage: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/shares/{share_id}/permissions")
async def update_share_permissions(
    share_id: int,
    permissions: List[str],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour les permissions d'un partage"""
    try:
        sharing_service = DocumentSharingService(db)
        share = sharing_service.update_share_permissions(share_id, current_user.id, permissions)
        
        return {
            "success": True,
            "message": "Permissions mises à jour",
            "share": {
                "id": share.id,
                "permissions": share.permissions,
                "updated_at": share.updated_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/shares/{share_id}/extend")
async def extend_share_expiration(
    share_id: int,
    new_expires_at: datetime,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Prolonge l'expiration d'un partage"""
    try:
        sharing_service = DocumentSharingService(db)
        share = sharing_service.extend_share_expiration(share_id, current_user.id, new_expires_at)
        
        return {
            "success": True,
            "message": "Expiration prolongée",
            "share": {
                "id": share.id,
                "expires_at": share.expires_at.isoformat(),
                "updated_at": share.updated_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la prolongation: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/shares/{share_id}")
async def revoke_share(
    share_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Révoque un partage"""
    try:
        sharing_service = DocumentSharingService(db)
        success = sharing_service.revoke_share(share_id, current_user.id)
        
        return {
            "success": True,
            "message": "Partage révoqué avec succès"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la révocation: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/shares/statistics")
async def get_share_statistics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les statistiques des partages"""
    try:
        sharing_service = DocumentSharingService(db)
        stats = sharing_service.get_share_statistics(current_user.id)
        
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/shares/cleanup")
async def cleanup_expired_shares(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Nettoie les partages expirés (admin seulement)"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Accès administrateur requis")
        
        sharing_service = DocumentSharingService(db)
        cleaned_count = sharing_service.cleanup_expired_shares()
        
        return {
            "success": True,
            "message": f"{cleaned_count} partages expirés nettoyés"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") 