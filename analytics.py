"""
Système d'analytics et métriques pour DocSearch AI
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import Session

from models import User, Document, ChatHistory, UserSession
from config import settings

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service d'analytics pour DocSearch AI"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Obtenir les statistiques d'un utilisateur spécifique"""
        try:
            # Statistiques de base
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "Utilisateur non trouvé"}
            
            # Documents uploadés
            documents_count = self.db.query(Document).filter(
                Document.user_id == user_id
            ).count()
            
            # Sessions créées
            sessions_count = self.db.query(UserSession).filter(
                UserSession.user_id == user_id
            ).count()
            
            # Questions posées
            questions_count = self.db.query(ChatHistory).filter(
                ChatHistory.user_id == user_id
            ).count()
            
            # Activité récente (7 derniers jours)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_activity = self.db.query(ChatHistory).filter(
                and_(
                    ChatHistory.user_id == user_id,
                    ChatHistory.created_at >= week_ago
                )
            ).count()
            
            # Types de documents les plus utilisés
            doc_types = self.db.query(
                Document.file_type,
                func.count(Document.id).label('count')
            ).filter(
                Document.user_id == user_id
            ).group_by(Document.file_type).order_by(desc('count')).limit(5).all()
            
            # Activité par jour (30 derniers jours)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            daily_activity = self.db.query(
                func.date(ChatHistory.created_at).label('date'),
                func.count(ChatHistory.id).label('count')
            ).filter(
                and_(
                    ChatHistory.user_id == user_id,
                    ChatHistory.created_at >= thirty_days_ago
                )
            ).group_by(func.date(ChatHistory.created_at)).order_by('date').all()
            
            return {
                "user_info": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_admin": user.is_admin,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                },
                "documents": {
                    "total": documents_count,
                    "types": [{"type": dt.file_type, "count": dt.count} for dt in doc_types]
                },
                "sessions": {
                    "total": sessions_count
                },
                "questions": {
                    "total": questions_count,
                    "recent_7_days": recent_activity
                },
                "activity": {
                    "daily": [{"date": str(da.date), "count": da.count} for da in daily_activity]
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats utilisateur: {e}")
            return {"error": str(e)}
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques globales de l'application"""
        try:
            # Statistiques utilisateurs
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.is_active == True).count()
            admin_users = self.db.query(User).filter(User.is_admin == True).count()
            
            # Nouveaux utilisateurs (30 derniers jours)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            new_users = self.db.query(User).filter(
                User.created_at >= thirty_days_ago
            ).count()
            
            # Statistiques documents
            total_documents = self.db.query(Document).count()
            total_sessions = self.db.query(UserSession).count()
            total_questions = self.db.query(ChatHistory).count()
            
            # Types de documents
            doc_types = self.db.query(
                Document.file_type,
                func.count(Document.id).label('count')
            ).group_by(Document.file_type).order_by(desc('count')).all()
            
            # Activité récente (7 derniers jours)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_questions = self.db.query(ChatHistory).filter(
                ChatHistory.created_at >= week_ago
            ).count()
            
            recent_uploads = self.db.query(Document).filter(
                Document.created_at >= week_ago
            ).count()
            
            # Top utilisateurs par activité
            top_users = self.db.query(
                User.username,
                func.count(ChatHistory.id).label('question_count')
            ).join(ChatHistory, User.id == ChatHistory.user_id).group_by(
                User.id, User.username
            ).order_by(desc('question_count')).limit(10).all()
            
            # Activité par jour (30 derniers jours)
            daily_activity = self.db.query(
                func.date(ChatHistory.created_at).label('date'),
                func.count(ChatHistory.id).label('count')
            ).filter(
                ChatHistory.created_at >= thirty_days_ago
            ).group_by(func.date(ChatHistory.created_at)).order_by('date').all()
            
            return {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "admins": admin_users,
                    "new_30_days": new_users
                },
                "documents": {
                    "total": total_documents,
                    "types": [{"type": dt.file_type, "count": dt.count} for dt in doc_types]
                },
                "sessions": {
                    "total": total_sessions
                },
                "questions": {
                    "total": total_questions,
                    "recent_7_days": recent_questions
                },
                "uploads": {
                    "recent_7_days": recent_uploads
                },
                "top_users": [
                    {"username": tu.username, "questions": tu.question_count} 
                    for tu in top_users
                ],
                "activity": {
                    "daily": [{"date": str(da.date), "count": da.count} for da in daily_activity]
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats globales: {e}")
            return {"error": str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtenir les métriques de performance"""
        try:
            # Temps de réponse moyen (approximatif)
            # Note: Dans une vraie application, on stockerait les temps de réponse
            avg_response_time = 2.5  # secondes (exemple)
            
            # Taux de succès des questions
            total_questions = self.db.query(ChatHistory).count()
            successful_questions = self.db.query(ChatHistory).filter(
                ChatHistory.answer.isnot(None)
            ).count()
            
            success_rate = (successful_questions / total_questions * 100) if total_questions > 0 else 0
            
            # Documents les plus consultés
            popular_docs = self.db.query(
                Document.filename,
                Document.file_type,
                func.count(ChatHistory.id).label('usage_count')
            ).join(ChatHistory, Document.session_id == ChatHistory.session_id).group_by(
                Document.id, Document.filename, Document.file_type
            ).order_by(desc('usage_count')).limit(10).all()
            
            # Utilisation par heure de la journée
            hourly_usage = self.db.query(
                func.extract('hour', ChatHistory.created_at).label('hour'),
                func.count(ChatHistory.id).label('count')
            ).group_by(func.extract('hour', ChatHistory.created_at)).order_by('hour').all()
            
            return {
                "performance": {
                    "avg_response_time": avg_response_time,
                    "success_rate": round(success_rate, 2)
                },
                "popular_documents": [
                    {
                        "filename": pd.filename,
                        "type": pd.file_type,
                        "usage_count": pd.usage_count
                    } for pd in popular_docs
                ],
                "hourly_usage": [
                    {"hour": int(hu.hour), "count": hu.count} for hu in hourly_usage
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des métriques de performance: {e}")
            return {"error": str(e)}
    
    def track_user_activity(self, user_id: int, action: str, details: Dict[str, Any] = None):
        """Tracker une activité utilisateur"""
        try:
            # Dans une vraie application, on créerait une table ActivityLog
            # Pour l'instant, on utilise les tables existantes
            logger.info(f"Activité utilisateur {user_id}: {action} - {details}")
            
        except Exception as e:
            logger.error(f"Erreur lors du tracking d'activité: {e}")
    
    def get_user_insights(self, user_id: int) -> Dict[str, Any]:
        """Obtenir des insights personnalisés pour un utilisateur"""
        try:
            # Questions les plus fréquentes
            common_questions = self.db.query(
                ChatHistory.question,
                func.count(ChatHistory.id).label('count')
            ).filter(
                ChatHistory.user_id == user_id
            ).group_by(ChatHistory.question).order_by(desc('count')).limit(5).all()
            
            # Sessions les plus actives
            active_sessions = self.db.query(
                UserSession.session_id,
                func.count(ChatHistory.id).label('question_count')
            ).join(ChatHistory, UserSession.session_id == ChatHistory.session_id).filter(
                UserSession.user_id == user_id
            ).group_by(UserSession.session_id).order_by(desc('question_count')).limit(5).all()
            
            # Recommandations basées sur l'usage
            recommendations = []
            
            # Si l'utilisateur pose beaucoup de questions sur des documents PDF
            pdf_questions = self.db.query(ChatHistory).join(
                Document, ChatHistory.session_id == Document.session_id
            ).filter(
                and_(
                    ChatHistory.user_id == user_id,
                    Document.file_type == 'pdf'
                )
            ).count()
            
            if pdf_questions > 10:
                recommendations.append("Vous utilisez beaucoup de documents PDF. Essayez d'uploader des documents Word ou Excel pour plus de variété.")
            
            # Si l'utilisateur n'a pas d'activité récente
            last_activity = self.db.query(ChatHistory).filter(
                ChatHistory.user_id == user_id
            ).order_by(desc(ChatHistory.created_at)).first()
            
            if last_activity and (datetime.utcnow() - last_activity.created_at).days > 7:
                recommendations.append("Vous n'avez pas utilisé DocSearch depuis plus d'une semaine. Revenez explorer vos documents !")
            
            return {
                "common_questions": [
                    {"question": cq.question, "count": cq.count} for cq in common_questions
                ],
                "active_sessions": [
                    {"session_id": str(as_.session_id), "questions": as_.question_count} 
                    for as_ in active_sessions
                ],
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des insights: {e}")
            return {"error": str(e)} 