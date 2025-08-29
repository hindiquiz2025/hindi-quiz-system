from flask import Blueprint, request, jsonify, render_template_string
from src.models.participant import db, Participant
from datetime import datetime
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def admin_dashboard():
    """Admin dashboard for managing participants and sending emails"""
    dashboard_html = """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>हिंदी राजभाषा प्रश्नोत्तरी - प्रशासन पैनल</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');
            body { font-family: 'Noto Sans Devanagari', sans-serif; }
        </style>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen">
            <!-- Header -->
            <header class="bg-orange-600 text-white shadow-lg">
                <div class="max-w-7xl mx-auto px-4 py-6">
                    <h1 class="text-3xl font-bold">हिंदी राजभाषा प्रश्नोत्तरी - प्रशासन पैनल</h1>
                    <p class="text-orange-100 mt-2">प्रतिभागी प्रबंधन और ईमेल भेजना</p>
                </div>
            </header>

            <div class="max-w-7xl mx-auto px-4 py-8">
                <!-- Stats Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="p-2 bg-blue-100 rounded-lg">
                                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                                </svg>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-600">कुल प्रतिभागी</p>
                                <p class="text-2xl font-semibold text-gray-900" id="total-participants">0</p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="p-2 bg-green-100 rounded-lg">
                                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-600">पूर्ण किए गए</p>
                                <p class="text-2xl font-semibold text-gray-900" id="completed-participants">0</p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="p-2 bg-yellow-100 rounded-lg">
                                <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-600">औसत स्कोर</p>
                                <p class="text-2xl font-semibold text-gray-900" id="average-score">0</p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="p-2 bg-purple-100 rounded-lg">
                                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
                                </svg>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-600">सर्वोच्च स्कोर</p>
                                <p class="text-2xl font-semibold text-gray-900" id="highest-score">0</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Email Section -->
                <div class="bg-white rounded-lg shadow mb-8">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h2 class="text-xl font-semibold text-gray-900">ईमेल भेजें</h2>
                    </div>
                    <div class="p-6">
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">प्रश्नोत्तरी URL</label>
                            <input type="url" id="quiz-url" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500" 
                                   value="http://localhost:3000" placeholder="प्रश्नोत्तरी का URL दर्ज करें">
                        </div>
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">ईमेल पते (प्रत्येक लाइन में एक)</label>
                            <textarea id="email-list" rows="6" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500" 
                                      placeholder="example1@email.com&#10;example2@email.com&#10;example3@email.com"></textarea>
                        </div>
                        <button onclick="sendEmails()" class="bg-orange-600 hover:bg-orange-700 text-white px-6 py-2 rounded-md font-medium">
                            ईमेल भेजें
                        </button>
                        <div id="email-status" class="mt-4"></div>
                    </div>
                </div>

                <!-- Participants Table -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                        <h2 class="text-xl font-semibold text-gray-900">प्रतिभागी सूची</h2>
                        <button onclick="refreshData()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                            रीफ्रेश करें
                        </button>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">नाम</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ईमेल</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">स्कोर</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">सही उत्तर</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">स्थिति</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">दिनांक</th>
                                </tr>
                            </thead>
                            <tbody id="participants-table" class="bg-white divide-y divide-gray-200">
                                <!-- Participants will be loaded here -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Load data on page load
            document.addEventListener('DOMContentLoaded', function() {
                refreshData();
            });

            async function refreshData() {
                try {
                    // Load stats
                    const statsResponse = await fetch('/api/quiz/participants/stats');
                    const statsData = await statsResponse.json();
                    
                    if (statsData.success) {
                        document.getElementById('total-participants').textContent = statsData.stats.total_participants;
                        document.getElementById('completed-participants').textContent = statsData.stats.completed_participants;
                        document.getElementById('average-score').textContent = statsData.stats.average_score;
                        document.getElementById('highest-score').textContent = statsData.stats.highest_score;
                    }

                    // Load participants
                    const participantsResponse = await fetch('/api/quiz/participants');
                    const participantsData = await participantsResponse.json();
                    
                    if (participantsData.success) {
                        const tbody = document.getElementById('participants-table');
                        tbody.innerHTML = '';
                        
                        participantsData.participants.forEach(participant => {
                            const row = document.createElement('tr');
                            const status = participant.completed_at ? 'पूर्ण' : 'प्रगति में';
                            const statusClass = participant.completed_at ? 'text-green-600 bg-green-100' : 'text-yellow-600 bg-yellow-100';
                            
                            row.innerHTML = `
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${participant.name}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${participant.email}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${participant.score}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${participant.correct_answers}/${participant.total_questions}</td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">
                                        ${status}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    ${new Date(participant.created_at).toLocaleDateString('hi-IN')}
                                </td>
                            `;
                            tbody.appendChild(row);
                        });
                    }
                } catch (error) {
                    console.error('Error loading data:', error);
                }
            }

            async function sendEmails() {
                const quizUrl = document.getElementById('quiz-url').value.trim();
                const emailText = document.getElementById('email-list').value.trim();
                const statusDiv = document.getElementById('email-status');
                
                if (!quizUrl || !emailText) {
                    statusDiv.innerHTML = '<div class="text-red-600">कृपया URL और ईमेल पते दर्ज करें।</div>';
                    return;
                }
                
                const emails = emailText.split('\\n').map(email => email.trim()).filter(email => email);
                
                if (emails.length === 0) {
                    statusDiv.innerHTML = '<div class="text-red-600">कोई वैध ईमेल पता नहीं मिला।</div>';
                    return;
                }
                
                statusDiv.innerHTML = '<div class="text-blue-600">ईमेल भेजे जा रहे हैं...</div>';
                
                try {
                    const response = await fetch('/api/quiz/send-quiz-email', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            emails: emails,
                            quiz_url: quizUrl
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        statusDiv.innerHTML = `
                            <div class="text-green-600">
                                <p>✅ ${data.sent_count} ईमेल सफलतापूर्वक भेजे गए</p>
                                ${data.failed_count > 0 ? `<p class="text-red-600">❌ ${data.failed_count} ईमेल भेजने में असफल</p>` : ''}
                            </div>
                        `;
                    } else {
                        statusDiv.innerHTML = `<div class="text-red-600">त्रुटि: ${data.error}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="text-red-600">नेटवर्क त्रुटि: ${error.message}</div>`;
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(dashboard_html)

