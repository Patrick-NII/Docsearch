'use client';

import React, { useState } from 'react';
import { useAuth } from './AuthContext';

export const UserProfile: React.FC = () => {
  const { user, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  if (!user) return null;

  const handleLogout = () => {
    logout();
    setIsDropdownOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-md p-2"
      >
        <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-medium">
            {user.full_name ? user.full_name.charAt(0).toUpperCase() : user.username.charAt(0).toUpperCase()}
          </span>
        </div>
        <div className="hidden md:block text-left">
          <div className="text-sm font-medium text-gray-900">
            {user.full_name || user.username}
          </div>
          <div className="text-xs text-gray-500">
            {user.email}
          </div>
        </div>
        <svg
          className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isDropdownOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50">
          <div className="py-1">
            <div className="px-4 py-2 border-b border-gray-100">
              <div className="text-sm font-medium text-gray-900">
                {user.full_name || user.username}
              </div>
              <div className="text-xs text-gray-500">
                {user.email}
              </div>
              {user.is_admin && (
                <div className="mt-1">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                    Administrateur
                  </span>
                </div>
              )}
            </div>

            <div className="px-4 py-2 text-xs text-gray-500">
              <div>Membre depuis : {new Date(user.created_at).toLocaleDateString('fr-FR')}</div>
              <div>Statut : {user.is_active ? 'Actif' : 'Inactif'}</div>
            </div>

            <div className="border-t border-gray-100">
              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Se déconnecter
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Overlay pour fermer le dropdown */}
      {isDropdownOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsDropdownOpen(false)}
        />
      )}
    </div>
  );
}; 