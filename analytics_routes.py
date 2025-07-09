"""
Routes pour les analytics et métriques de DocSearch AI
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from auth import get_current_user, get_current_admin_user
from models import User, get_db
from analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/user/stats")
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques personnelles de l'utilisateur"""
    try:
        analytics = AnalyticsService(db)
        stats = analytics.get_user_stats(current_user.id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")

@router.get("/user/insights")
async def get_user_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtenir des insights personnalisés pour l'utilisateur"""
    try:
        analytics = AnalyticsService(db)
        insights = analytics.get_user_insights(current_user.id)
        
        if "error" in insights:
            raise HTTPException(status_code=404, detail=insights["error"])
        
        return {
            "success": True,
            "data": insights,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des insights: {str(e)}")

@router.get("/global/stats")
async def get_global_analytics(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques globales de l'application (admin uniquement)"""
    try:
        analytics = AnalyticsService(db)
        stats = analytics.get_global_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques globales: {str(e)}")

@router.get("/performance")
async def get_performance_metrics(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtenir les métriques de performance (admin uniquement)"""
    try:
        analytics = AnalyticsService(db)
        metrics = analytics.get_performance_metrics()
        
        if "error" in metrics:
            raise HTTPException(status_code=404, detail=metrics["error"])
        
        return {
            "success": True,
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métriques de performance: {str(e)}")

@router.get("/user/{user_id}/stats")
async def get_specific_user_analytics(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques d'un utilisateur spécifique (admin uniquement)"""
    try:
        analytics = AnalyticsService(db)
        stats = analytics.get_user_stats(user_id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques utilisateur: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtenir les données pour le tableau de bord utilisateur"""
    try:
        analytics = AnalyticsService(db)
        
        # Statistiques personnelles
        user_stats = analytics.get_user_stats(current_user.id)
        user_insights = analytics.get_user_insights(current_user.id)
        
        # Statistiques globales (si admin)
        global_stats = None
        if current_user.is_admin:
            global_stats = analytics.get_global_stats()
        
        dashboard_data = {
            "user_stats": user_stats,
            "user_insights": user_insights,
            "global_stats": global_stats if current_user.is_admin else None,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données du tableau de bord: {str(e)}")

@router.get("/activity/summary")
async def get_activity_summary(
    days: int = Query(7, description="Nombre de jours pour le résumé"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtenir un résumé de l'activité récente"""
    try:
        if days > 30:
            raise HTTPException(status_code=400, detail="Le nombre de jours ne peut pas dépasser 30")
        
        analytics = AnalyticsService(db)
        
        # Calculer la date de début
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Statistiques d'activité récente
        from sqlalchemy import and_
        from models import ChatHistory, Document, UserSession
        
        recent_questions = db.query(ChatHistory).filter(
            and_(
                ChatHistory.user_id == current_user.id,
                ChatHistory.created_at >= start_date
            )
        ).count()
        
        recent_uploads = db.query(Document).filter(
            and_(
                Document.user_id == current_user.id,
                Document.created_at >= start_date
            )
        ).count()
        
        recent_sessions = db.query(UserSession).filter(
            and_(
                UserSession.user_id == current_user.id,
                UserSession.created_at >= start_date
            )
        ).count()
        
        summary = {
            "period_days": days,
            "questions_asked": recent_questions,
            "documents_uploaded": recent_uploads,
            "sessions_created": recent_sessions,
            "avg_questions_per_day": round(recent_questions / days, 2) if days > 0 else 0,
            "most_active_day": None,  # À implémenter si nécessaire
            "activity_trend": "stable"  # À calculer basé sur les données
        }
        
        return {
            "success": True,
            "data": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du résumé d'activité: {str(e)}")

@router.post("/track")
async def track_activity(
    action: str,
    details: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tracker une activité utilisateur"""
    try:
        analytics = AnalyticsService(db)
        analytics.track_user_activity(current_user.id, action, details or {})
        
        return {
            "success": True,
            "message": "Activité trackée avec succès",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du tracking d'activité: {str(e)}") 