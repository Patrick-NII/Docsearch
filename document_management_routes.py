"""
Routes pour la gestion avancée des documents de DocSearch AI
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from auth import get_current_user, get_current_admin_user
from models import User, get_db
from document_versioning import DocumentVersioningService
from document_annotations import DocumentAnnotationService, DocumentTagService
from document_sharing import DocumentSharingService

router = APIRouter(prefix="/documents", tags=["document-management"])

# ==================== VERSIONING ====================

@router.get("/{document_id}/versions")
async def get_document_versions(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère toutes les versions d'un document"""
    try:
        versioning_service = DocumentVersioningService(db)
        versions = versioning_service.get_document_versions(document_id)
        
        # Vérifier les permissions
        if not versioning_service.check_permission(document_id, current_user.id, "read"):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        version_data = []
        for version in versions:
            version_data.append({
                "id": version.id,
                "version_number": version.version_number,
                "filename": version.filename,
                "file_type": version.file_type,
                "file_size": version.file_size,
                "uploaded_by": version.uploaded_by,
                "created_at": version.created_at.isoformat(),
                "metadata": version.metadata
            })
        
        return {
            "success": True,
            "data": version_data,
            "total_versions": len(version_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des versions: {str(e)}")

@router.get("/versions/{version_id}")
async def get_version_details(
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les détails d'une version spécifique"""
    try:
        versioning_service = DocumentVersioningService(db)
        version = versioning_service.get_version(version_id)
        
        if not version:
            raise HTTPException(status_code=404, detail="Version non trouvée")
        
        # Vérifier les permissions
        if not versioning_service.check_permission(version.document_id, current_user.id, "read"):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        return {
            "success": True,
            "data": {
                "id": version.id,
                "document_id": version.document_id,
                "version_number": version.version_number,
                "filename": version.filename,
                "file_type": version.file_type,
                "file_size": version.file_size,
                "file_hash": version.file_hash,
                "uploaded_by": version.uploaded_by,
                "created_at": version.created_at.isoformat(),
                "metadata": version.metadata
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la version: {str(e)}")

@router.post("/{document_id}/versions")
async def create_new_version(
    document_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée une nouvelle version d'un document"""
    try:
        # Vérifier les permissions
        versioning_service = DocumentVersioningService(db)
        if not versioning_service.check_permission(document_id, current_user.id, "write"):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Lire le contenu du fichier
        file_content = await file.read()
        
        # Créer la nouvelle version
        new_version = versioning_service.create_version(
            document_id=document_id,
            file_content=file_content,
            filename=file.filename,
            file_type=file.filename.split('.')[-1] if '.' in file.filename else 'unknown',
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": {
                "id": new_version.id,
                "version_number": new_version.version_number,
                "filename": new_version.filename,
                "created_at": new_version.created_at.isoformat()
            },
            "message": f"Nouvelle version {new_version.version_number} créée"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la version: {str(e)}")

@router.get("/versions/{version1_id}/compare/{version2_id}")
async def compare_versions(
    version1_id: int,
    version2_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare deux versions d'un document"""
    try:
        versioning_service = DocumentVersioningService(db)
        comparison = versioning_service.compare_versions(version1_id, version2_id)
        
        if "error" in comparison:
            raise HTTPException(status_code=404, detail=comparison["error"])
        
        return {
            "success": True,
            "data": comparison
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la comparaison: {str(e)}")

@router.post("/versions/{version_id}/restore")
async def restore_version(
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restaure une version précédente"""
    try:
        versioning_service = DocumentVersioningService(db)
        version = versioning_service.get_version(version_id)
        
        if not version:
            raise HTTPException(status_code=404, detail="Version non trouvée")
        
        # Vérifier les permissions
        if not versioning_service.check_permission(version.document_id, current_user.id, "write"):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        success = versioning_service.restore_version(version_id, current_user.id)
        
        if success:
            return {
                "success": True,
                "message": f"Version {version.version_number} restaurée avec succès"
            }
        else:
            raise HTTPException(status_code=400, detail="Impossible de restaurer la version")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la restauration: {str(e)}")

# ==================== ANNOTATIONS ====================

@router.post("/{document_id}/annotations")
async def create_annotation(
    document_id: int,
    content: str = Form(...),
    annotation_type: str = Form("note"),
    position: str = Form("{}"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée une nouvelle annotation sur un document"""
    try:
        annotation_service = DocumentAnnotationService(db)
        
        # Vérifier les permissions
        if not annotation_service.check_permission(document_id, current_user.id, "comment"):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Parser la position JSON
        try:
            position_data = json.loads(position)
        except json.JSONDecodeError:
            position_data = {}
        
        annotation = annotation_service.create_annotation(
            document_id=document_id,
            user_id=current_user.id,
            content=content,
            annotation_type=annotation_type,
            position=position_data
        )
        
        return {
            "success": True,
            "data": {
                "id": annotation.id,
                "content": annotation.content,
                "annotation_type": annotation.annotation_type,
                "created_at": annotation.created_at.isoformat()
            },
            "message": "Annotation créée avec succès"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'annotation: {str(e)}")

@router.get("/{document_id}/annotations")
async def get_document_annotations(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère toutes les annotations d'un document"""
    try:
        annotation_service = DocumentAnnotationService(db)
        
        # Vérifier les permissions
        if not annotation_service.check_permission(document_id, current_user.id, "read"):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        annotations = annotation_service.get_document_annotations(document_id)
        
        annotation_data = []
        for annotation in annotations:
            annotation_data.append({
                "id": annotation.id,
                "content": annotation.content,
                "annotation_type": annotation.annotation_type,
                "position": annotation.position,
                "user_id": annotation.user_id,
                "created_at": annotation.created_at.isoformat(),
                "updated_at": annotation.updated_at.isoformat() if annotation.updated_at else None
            })
        
        return {
            "success": True,
            "data": annotation_data,
            "total_annotations": len(annotation_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des annotations: {str(e)}")

@router.put("/annotations/{annotation_id}")
async def update_annotation(
    annotation_id: int,
    content: str = Form(...),
    annotation_type: str = Form("note"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour une annotation"""
    try:
        annotation_service = DocumentAnnotationService(db)
        
        success = annotation_service.update_annotation(
            annotation_id=annotation_id,
            user_id=current_user.id,
            content=content,
            annotation_type=annotation_type
        )
        
        if success:
            return {
                "success": True,
                "message": "Annotation mise à jour avec succès"
            }
        else:
            raise HTTPException(status_code=403, detail="Impossible de modifier cette annotation")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@router.delete("/annotations/{annotation_id}")
async def delete_annotation(
    annotation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime une annotation"""
    try:
        annotation_service = DocumentAnnotationService(db)
        
        success = annotation_service.delete_annotation(annotation_id, current_user.id)
        
        if success:
            return {
                "success": True,
                "message": "Annotation supprimée avec succès"
            }
        else:
            raise HTTPException(status_code=403, detail="Impossible de supprimer cette annotation")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

# ==================== TAGS ====================

@router.post("/tags")
async def create_tag(
    name: str = Form(...),
    color: str = Form("#3B82F6"),
    description: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un nouveau tag"""
    try:
        tag_service = DocumentTagService(db)
        tag = tag_service.create_tag(name=name, color=color, description=description)
        
        return {
            "success": True,
            "data": {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "description": tag.description
            },
            "message": f"Tag '{name}' créé avec succès"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du tag: {str(e)}")

@router.get("/tags")
async def get_all_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère tous les tags"""
    try:
        tag_service = DocumentTagService(db)
        tags = tag_service.get_all_tags()
        
        tag_data = []
        for tag in tags:
            tag_data.append({
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "description": tag.description,
                "created_at": tag.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": tag_data,
            "total_tags": len(tag_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des tags: {str(e)}")

@router.post("/{document_id}/tags/{tag_id}")
async def add_tag_to_document(
    document_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ajoute un tag à un document"""
    try:
        tag_service = DocumentTagService(db)
        
        # Vérifier les permissions
        if not tag_service.check_permission(document_id, current_user.id, "write"):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        success = tag_service.add_tag_to_document(document_id, tag_id)
        
        if success:
            return {
                "success": True,
                "message": "Tag ajouté au document avec succès"
            }
        else:
            raise HTTPException(status_code=400, detail="Impossible d'ajouter le tag")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout du tag: {str(e)}")

@router.delete("/{document_id}/tags/{tag_id}")
async def remove_tag_from_document(
    document_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retire un tag d'un document"""
    try:
        tag_service = DocumentTagService(db)
        
        # Vérifier les permissions
        if not tag_service.check_permission(document_id, current_user.id, "write"):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        success = tag_service.remove_tag_from_document(document_id, tag_id)
        
        if success:
            return {
                "success": True,
                "message": "Tag retiré du document avec succès"
            }
        else:
            raise HTTPException(status_code=400, detail="Impossible de retirer le tag")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du retrait du tag: {str(e)}")

# ==================== PARTAGE ====================

@router.post("/{document_id}/share")
async def share_document(
    document_id: int,
    shared_with_id: int = Form(...),
    permissions: str = Form('["read"]'),
    expires_at: str = Form(None),
    message: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Partage un document avec un autre utilisateur"""
    try:
        sharing_service = DocumentSharingService(db)
        
        # Parser les permissions JSON
        try:
            permissions_list = json.loads(permissions)
        except json.JSONDecodeError:
            permissions_list = ["read"]
        
        # Parser la date d'expiration
        expires_date = None
        if expires_at:
            try:
                expires_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Format de date invalide")
        
        share = sharing_service.share_document(
            document_id=document_id,
            owner_id=current_user.id,
            shared_with_id=shared_with_id,
            permissions=permissions_list,
            expires_at=expires_date,
            message=message
        )
        
        return {
            "success": True,
            "data": {
                "id": share.id,
                "document_id": share.document_id,
                "shared_with": share.shared_with,
                "permissions": share.permissions,
                "expires_at": share.expires_at.isoformat() if share.expires_at else None,
                "message": share.message,
                "created_at": share.created_at.isoformat()
            },
            "message": "Document partagé avec succès"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du partage: {str(e)}")

@router.get("/shared")
async def get_shared_documents(
    as_owner: bool = Query(False, description="Récupérer les documents partagés par l'utilisateur"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les documents partagés"""
    try:
        sharing_service = DocumentSharingService(db)
        shares = sharing_service.get_shared_documents(current_user.id, as_owner=as_owner)
        
        share_data = []
        for share in shares:
            share_data.append({
                "id": share.id,
                "document_id": share.document_id,
                "owner_id": share.owner_id,
                "shared_with": share.shared_with,
                "permissions": share.permissions,
                "expires_at": share.expires_at.isoformat() if share.expires_at else None,
                "message": share.message,
                "created_at": share.created_at.isoformat(),
                "is_expired": share.expires_at and share.expires_at < datetime.utcnow()
            })
        
        return {
            "success": True,
            "data": share_data,
            "total_shares": len(share_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des partages: {str(e)}")

@router.delete("/shares/{share_id}")
async def revoke_share(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Révoque un partage de document"""
    try:
        sharing_service = DocumentSharingService(db)
        
        success = sharing_service.revoke_share(share_id, current_user.id)
        
        if success:
            return {
                "success": True,
                "message": "Partage révoqué avec succès"
            }
        else:
            raise HTTPException(status_code=403, detail="Impossible de révoquer ce partage")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la révocation: {str(e)}")

# ==================== STATISTIQUES ====================

@router.get("/{document_id}/version-stats")
async def get_version_statistics(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les statistiques des versions d'un document"""
    try:
        versioning_service = DocumentVersioningService(db)
        
        # Vérifier les permissions
        if not versioning_service.check_permission(document_id, current_user.id, "read"):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        stats = versioning_service.get_version_statistics(document_id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")

@router.get("/tag-statistics")
async def get_tag_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les statistiques des tags"""
    try:
        tag_service = DocumentTagService(db)
        stats = tag_service.get_tag_statistics()
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")

@router.get("/share-statistics")
async def get_share_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les statistiques de partage"""
    try:
        sharing_service = DocumentSharingService(db)
        stats = sharing_service.get_share_statistics(current_user.id)
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}") 