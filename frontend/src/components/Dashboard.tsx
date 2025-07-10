'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import axios from 'axios';

interface DashboardData {
  user_stats: any;
  user_insights: any;
  global_stats?: any;
  last_updated: string;
}

interface ActivitySummary {
  period_days: number;
  questions_asked: number;
  documents_uploaded: number;
  sessions_created: number;
  avg_questions_per_day: number;
  activity_trend: string;
}

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [activitySummary, setActivitySummary] = useState<ActivitySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState(7);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadDashboardData();
    loadActivitySummary(selectedPeriod);
  }, [selectedPeriod]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/analytics/dashboard`);
      setDashboardData(response.data.data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors du chargement du tableau de bord');
    } finally {
      setLoading(false);
    }
  };

  const loadActivitySummary = async (days: number) => {
    try {
      const response = await axios.get(`${API_URL}/analytics/activity/summary?days=${days}`);
      setActivitySummary(response.data.data);
    } catch (error: any) {
      console.error('Erreur lors du chargement du résumé d\'activité:', error);
    }
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('fr-FR').format(num);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Erreur</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return <div>Aucune donnée disponible</div>;
  }

  return (
    <div className="space-y-6">
      {/* En-tête du tableau de bord */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Tableau de bord
            </h1>
            <p className="text-gray-600">
              Bienvenue, {user?.full_name || user?.username} !
            </p>
          </div>
          <div className="text-sm text-gray-500">
            Dernière mise à jour : {formatDate(dashboardData.last_updated)}
          </div>
        </div>
      </div>

      {/* Statistiques personnelles */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Documents</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatNumber(dashboardData?.user_stats?.documents?.total ?? 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Questions</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatNumber(dashboardData?.user_stats?.questions?.total ?? 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-md flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Sessions</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatNumber(dashboardData?.user_stats?.sessions?.total ?? 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-orange-100 rounded-md flex items-center justify-center">
                <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Activité (7j)</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatNumber(dashboardData?.user_stats?.questions?.recent_7_days ?? 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Résumé d'activité */}
      {activitySummary && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Résumé d'activité</h2>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(Number(e.target.value))}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm"
            >
              <option value={7}>7 derniers jours</option>
              <option value={14}>14 derniers jours</option>
              <option value={30}>30 derniers jours</option>
            </select>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{activitySummary.questions_asked}</p>
              <p className="text-sm text-gray-600">Questions posées</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{activitySummary.documents_uploaded}</p>
              <p className="text-sm text-gray-600">Documents uploadés</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{activitySummary.avg_questions_per_day}</p>
              <p className="text-sm text-gray-600">Questions/jour (moyenne)</p>
            </div>
          </div>
        </div>
      )}

      {/* Types de documents */}
      {(dashboardData?.user_stats?.documents?.types?.length ?? 0) > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Types de documents</h2>
          <div className="space-y-3">
            {dashboardData?.user_stats?.documents?.types?.map?.((docType: any, index: number) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-indigo-500 rounded-full mr-3"></div>
                  <span className="text-sm font-medium text-gray-700">{docType.type.toUpperCase()}</span>
                </div>
                <span className="text-sm text-gray-500">{docType.count} documents</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Insights et recommandations */}
      {(dashboardData?.user_insights?.recommendations?.length ?? 0) > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recommandations</h2>
          <div className="space-y-3">
            {dashboardData?.user_insights?.recommendations?.map?.((recommendation: string, index: number) => (
              <div key={index} className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="w-5 h-5 text-blue-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p className="ml-3 text-sm text-gray-700">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Statistiques globales (admin uniquement) */}
      {user?.is_admin && dashboardData.global_stats && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Statistiques globales (Admin)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-indigo-600">{formatNumber(dashboardData?.global_stats?.users?.total ?? 0)}</p>
              <p className="text-sm text-gray-600">Utilisateurs totaux</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{formatNumber(dashboardData?.global_stats?.documents?.total ?? 0)}</p>
              <p className="text-sm text-gray-600">Documents totaux</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{formatNumber(dashboardData?.global_stats?.questions?.total ?? 0)}</p>
              <p className="text-sm text-gray-600">Questions totales</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">{formatNumber(dashboardData?.global_stats?.users?.new_30_days ?? 0)}</p>
              <p className="text-sm text-gray-600">Nouveaux (30j)</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 