"""
User Feedback Manager for v1.1
Handles user feedback, ratings, and learning from interactions.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from familycli.database.db_manager import DatabaseManager
from familycli.database.models import UserFeedback, Message, Session
from familycli.personas.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class FeedbackManager:
    """Manages user feedback and learning from interactions."""

    def __init__(self):
        self.db = DatabaseManager()
        self.memory_manager = MemoryManager()

    def submit_feedback(self, user_id: int, session_id: Optional[int] = None,
                       message_id: Optional[int] = None, rating: int = 5,
                       feedback_type: str = 'thumbs_up', comment: Optional[str] = None) -> bool:
        """Submit user feedback for a response."""
        session = self.db.get_session()
        try:
            feedback = UserFeedback(
                user_id=user_id,
                session_id=session_id,
                message_id=message_id,
                rating=rating,
                feedback_type=feedback_type,
                comment=comment
            )
            session.add(feedback)
            session.commit()

            # Learn from feedback
            self._learn_from_feedback(feedback)

            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to submit feedback: {e}")
            return False
        finally:
            session.close()

    def get_feedback_stats(self, user_id: int) -> Dict[str, Any]:
        """Get feedback statistics for a user."""
        session = self.db.get_session()
        try:
            feedbacks = session.query(UserFeedback).filter_by(user_id=user_id).all()

            if not feedbacks:
                return {
                    'total_feedback': 0,
                    'average_rating': 0,
                    'feedback_types': {},
                    'recent_feedback': []
                }

            total_rating = sum(f.rating for f in feedbacks)
            feedback_types = {}

            for feedback in feedbacks:
                fb_type = feedback.feedback_type
                feedback_types[fb_type] = feedback_types.get(fb_type, 0) + 1

            # Get recent feedback (last 10)
            recent_feedback = feedbacks[-10:]

            return {
                'total_feedback': len(feedbacks),
                'average_rating': round(total_rating / len(feedbacks), 1),
                'feedback_types': feedback_types,
                'recent_feedback': [{
                    'rating': f.rating,
                    'type': f.feedback_type,
                    'comment': f.comment,
                    'created_at': f.created_at.isoformat() if f.created_at else None
                } for f in recent_feedback]
            }
        finally:
            session.close()

    def get_feedback_for_session(self, session_id: int) -> List[Dict[str, Any]]:
        """Get all feedback for a specific session."""
        session = self.db.get_session()
        try:
            feedbacks = session.query(UserFeedback).filter_by(session_id=session_id).all()

            return [{
                'feedback_id': f.feedback_id,
                'rating': f.rating,
                'type': f.feedback_type,
                'comment': f.comment,
                'created_at': f.created_at.isoformat() if f.created_at else None
            } for f in feedbacks]
        finally:
            session.close()

    def _learn_from_feedback(self, feedback: UserFeedback) -> None:
        """Learn from user feedback to improve responses."""
        try:
            if feedback.rating <= 2:  # Low rating
                # Get the message that was rated poorly
                if feedback.message_id:
                    session = self.db.get_session()
                    try:
                        message = session.query(Message).filter_by(message_id=feedback.message_id).first()
                        if message and message.sender_id:  # AI response
                            # Store learning about what not to do
                            self.memory_manager.store_memory(
                                persona_id=message.sender_id,
                                memory_type='feedback_learning',
                                memory_key='negative_feedback',
                                memory_value=f"Response rated {feedback.rating}/5: {feedback.comment or 'No comment'}",
                                confidence=90
                            )
                    finally:
                        session.close()

            elif feedback.rating >= 4:  # High rating
                if feedback.message_id:
                    session = self.db.get_session()
                    try:
                        message = session.query(Message).filter_by(message_id=feedback.message_id).first()
                        if message and message.sender_id:
                            # Store positive learning
                            self.memory_manager.store_memory(
                                persona_id=message.sender_id,
                                memory_type='feedback_learning',
                                memory_key='positive_feedback',
                                memory_value=f"Well-received response pattern",
                                confidence=85
                            )
                    finally:
                        session.close()

        except Exception as e:
            logger.error(f"Failed to learn from feedback: {e}")

    def get_feedback_trends(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get feedback trends over time."""
        from datetime import timedelta

        session = self.db.get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            feedbacks = session.query(UserFeedback).filter(
                UserFeedback.user_id == user_id,
                UserFeedback.created_at >= cutoff_date
            ).all()

            if not feedbacks:
                return {'period': f'{days} days', 'total_feedback': 0, 'trends': []}

            # Group by date
            daily_stats = {}
            for feedback in feedbacks:
                date_key = feedback.created_at.date().isoformat() if feedback.created_at else 'unknown'
                if date_key not in daily_stats:
                    daily_stats[date_key] = {
                        'date': date_key,
                        'total': 0,
                        'average_rating': 0,
                        'positive': 0,
                        'negative': 0
                    }

                daily_stats[date_key]['total'] += 1
                daily_stats[date_key]['average_rating'] += feedback.rating

                if feedback.rating >= 4:
                    daily_stats[date_key]['positive'] += 1
                elif feedback.rating <= 2:
                    daily_stats[date_key]['negative'] += 1

            # Calculate averages
            for stats in daily_stats.values():
                if stats['total'] > 0:
                    stats['average_rating'] = round(stats['average_rating'] / stats['total'], 1)

            return {
                'period': f'{days} days',
                'total_feedback': len(feedbacks),
                'trends': list(daily_stats.values())
            }
        finally:
            session.close()

    def suggest_improvements(self, user_id: int) -> List[str]:
        """Suggest improvements based on feedback patterns."""
        stats = self.get_feedback_stats(user_id)
        suggestions = []

        if stats['total_feedback'] == 0:
            return ["Start providing feedback to help improve responses!"]

        avg_rating = stats['average_rating']

        if avg_rating < 3.0:
            suggestions.append("Consider adjusting persona personalities to better match your preferences")
            suggestions.append("Try different conversation topics that might engage better")

        if stats['feedback_types'].get('thumbs_down', 0) > stats['feedback_types'].get('thumbs_up', 0):
            suggestions.append("More negative than positive feedback - consider reviewing response quality")

        # Check for common negative feedback patterns
        recent_feedback = stats['recent_feedback']
        low_ratings = [f for f in recent_feedback if f['rating'] <= 2]

        if len(low_ratings) > len(recent_feedback) * 0.5:
            suggestions.append("Recent responses have been rated poorly - consider changing conversation style")

        if not suggestions:
            suggestions.append("Overall feedback is positive! Keep up the good conversations.")

        return suggestions

    def export_feedback_data(self, user_id: int, format_type: str = 'json') -> Optional[str]:
        """Export feedback data for analysis."""
        import json
        import csv
        from io import StringIO

        session = self.db.get_session()
        try:
            feedbacks = session.query(UserFeedback).filter_by(user_id=user_id).all()

            if format_type == 'json':
                data = [{
                    'feedback_id': f.feedback_id,
                    'session_id': f.session_id,
                    'message_id': f.message_id,
                    'rating': f.rating,
                    'type': f.feedback_type,
                    'comment': f.comment,
                    'created_at': f.created_at.isoformat() if f.created_at else None
                } for f in feedbacks]

                return json.dumps(data, indent=2)

            elif format_type == 'csv':
                output = StringIO()
                writer = csv.writer(output)

                # Write header
                writer.writerow(['Feedback ID', 'Session ID', 'Message ID', 'Rating', 'Type', 'Comment', 'Created At'])

                # Write data
                for f in feedbacks:
                    writer.writerow([
                        f.feedback_id,
                        f.session_id,
                        f.message_id,
                        f.rating,
                        f.feedback_type,
                        f.comment,
                        f.created_at.isoformat() if f.created_at else ''
                    ])

                return output.getvalue()

        finally:
            session.close()

        return None
