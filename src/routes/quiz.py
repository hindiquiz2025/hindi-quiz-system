from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.participant import Participant
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/participants', methods=['GET'])
def get_participants():
    """Get all participants with their scores"""
    try:
        participants = Participant.query.order_by(Participant.created_at.desc()).all()
        return jsonify({
            'success': True,
            'participants': [p.to_dict() for p in participants],
            'total_count': len(participants)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@quiz_bp.route('/participants/stats', methods=['GET'])
def get_participant_stats():
    """Get participant statistics"""
    try:
        total_participants = Participant.query.count()
        completed_participants = Participant.query.filter(Participant.completed_at.isnot(None)).count()
        
        if completed_participants > 0:
            avg_score = db.session.query(db.func.avg(Participant.score)).filter(
                Participant.completed_at.isnot(None)
            ).scalar() or 0
            
            highest_score = db.session.query(db.func.max(Participant.score)).filter(
                Participant.completed_at.isnot(None)
            ).scalar() or 0
        else:
            avg_score = 0
            highest_score = 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_participants': total_participants,
                'completed_participants': completed_participants,
                'average_score': round(avg_score, 2),
                'highest_score': highest_score
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@quiz_bp.route('/participants', methods=['POST'])
def register_participant():
    """Register a new participant"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        department = data.get('department', '').strip()
        post = data.get('post', '').strip()
        email = data.get('email', '').strip()
        mobile = data.get('mobile', '').strip()
        
        if not all([name, department, post, email, mobile]):
            return jsonify({'success': False, 'error': 'सभी फ़ील्ड आवश्यक हैं'}), 400
        
        # Check if participant already exists
        existing = Participant.query.filter_by(email=email).first()
        if existing:
            return jsonify({'success': False, 'error': 'यह ईमेल पहले से पंजीकृत है'}), 400
        
        participant = Participant(
            name=name, 
            department=department,
            post=post,
            email=email, 
            mobile=mobile
        )
        db.session.add(participant)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'participant': participant.to_dict(),
            'message': 'प्रतिभागी सफलतापूर्वक पंजीकृत'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@quiz_bp.route('/participants/<int:participant_id>/submit', methods=['POST'])
def submit_quiz_results():
    """Submit quiz results for a participant"""
    try:
        data = request.get_json()
        participant_id = data.get('participant_id')
        score = data.get('score', 0)
        correct_answers = data.get('correct_answers', 0)
        time_taken = data.get('time_taken', 0)
        answers = data.get('answers', [])
        
        participant = Participant.query.get(participant_id)
        if not participant:
            return jsonify({'success': False, 'error': 'प्रतिभागी नहीं मिला'}), 404
        
        participant.score = score
        participant.correct_answers = correct_answers
        participant.time_taken = time_taken
        participant.set_answers(answers)
        participant.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'participant': participant.to_dict(),
            'message': 'परिणाम सफलतापूर्वक सबमिट किए गए'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@quiz_bp.route('/send-quiz-email', methods=['POST'])
def send_quiz_email():
    """Send quiz invitation email to participants"""
    try:
        data = request.get_json()
        email_list = data.get('emails', [])
        quiz_url = data.get('quiz_url', 'http://localhost:3000')
        
        if not email_list:
            return jsonify({'success': False, 'error': 'ईमेल सूची आवश्यक है'}), 400
        
        # Email configuration (you would need to set up SMTP credentials)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')
        sender_password = os.getenv('SENDER_PASSWORD', 'your-app-password')
        
        subject = "हिंदी राजभाषा प्रश्नोत्तरी में भाग लें"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #ff6600; text-align: center;">हिंदी राजभाषा प्रश्नोत्तरी</h2>
                
                <p>नमस्कार,</p>
                
                <p>आपको हिंदी राजभाषा, इतिहास और संस्कृति पर आधारित एक रोचक प्रश्नोत्तरी में भाग लेने के लिए आमंत्रित किया जा रहा है।</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #ff6600;">प्रश्नोत्तरी की विशेषताएं:</h3>
                    <ul>
                        <li>कुल प्रश्न: 25</li>
                        <li>समय सीमा: प्रत्येक प्रश्न के लिए 7 सेकंड</li>
                        <li>अंक प्रणाली: सही उत्तर +3, गलत उत्तर -1</li>
                        <li>भाषा: हिंदी (देवनागरी)</li>
                        <li>कोई वापसी विकल्प नहीं</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{quiz_url}" style="background-color: #ff6600; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">प्रश्नोत्तरी शुरू करें</a>
                </div>
                
                <p>कृपया अपना नाम और ईमेल पता सही तरीके से दर्ज करें।</p>
                
                <p>शुभकामनाएं!</p>
                
                <hr style="margin: 30px 0;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    यह एक स्वचालित ईमेल है। कृपया इसका उत्तर न दें।
                </p>
            </div>
        </body>
        </html>
        """
        
        sent_count = 0
        failed_emails = []
        
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            
            for email in email_list:
                try:
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = sender_email
                    msg['To'] = email
                    
                    html_part = MIMEText(html_body, 'html', 'utf-8')
                    msg.attach(html_part)
                    
                    server.send_message(msg)
                    sent_count += 1
                except Exception as e:
                    failed_emails.append({'email': email, 'error': str(e)})
            
            server.quit()
            
        except Exception as e:
            return jsonify({
                'success': False, 
                'error': f'ईमेल सर्वर कनेक्शन त्रुटि: {str(e)}'
            }), 500
        
        return jsonify({
            'success': True,
            'sent_count': sent_count,
            'failed_count': len(failed_emails),
            'failed_emails': failed_emails,
            'message': f'{sent_count} ईमेल सफलतापूर्वक भेजे गए'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@quiz_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get top performers leaderboard"""
    try:
        top_participants = Participant.query.filter(
            Participant.completed_at.isnot(None)
        ).order_by(
            Participant.score.desc(),
            Participant.time_taken.asc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'leaderboard': [p.to_dict() for p in top_participants]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

