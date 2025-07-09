import React from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRightIcon, SparklesIcon, DocumentTextIcon, ChatBubbleLeftRightIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import Button from '../ui/Button';

interface HeroProps {
  onGetStarted?: () => void;
  onLearnMore?: () => void;
}

export default function Hero({ onGetStarted, onLearnMore }: HeroProps) {
  const router = useRouter();

  const handleGetStarted = () => {
    if (onGetStarted) {
      onGetStarted();
    } else {
      router.push('/login');
    }
  };

  const handleLearnMore = () => {
    if (onLearnMore) {
      onLearnMore();
    } else {
      // Scroll vers une section d'info ou ouvrir une modal
      console.log('En savoir plus');
    }
  };

  const features = [
    {
      icon: DocumentTextIcon,
      title: "Analyse de Documents",
      description: "Upload et analysez vos documents avec notre IA avancée"
    },
    {
      icon: ChatBubbleLeftRightIcon,
      title: "Chat Intelligent",
      description: "Posez des questions et obtenez des réponses précises"
    },
    {
      icon: ChartBarIcon,
      title: "Analytics Avancés",
      description: "Suivez vos performances et insights en temps réel"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Main Content */}
      <div className="flex flex-col items-center justify-center min-h-screen px-4 py-16">
        <div className="text-center mb-12 max-w-3xl mx-auto px-2">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-50 rounded-full border border-blue-200 mb-6">
            <SparklesIcon className="w-4 h-4 text-blue-600" />
            <span className="text-blue-700 text-xs font-medium">Nouveau : IA Avancée</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4 leading-tight">
            <span className="text-blue-600">
              DocSearch AI
            </span>
          </h1>
          
          <p className="text-base md:text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            L'assistant IA intelligent qui transforme vos documents en insights actionnables. 
            Posez des questions, obtenez des réponses précises.
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 mb-12 justify-center">
          <Button
            onClick={handleGetStarted}
            size="lg"
            icon={<ArrowRightIcon className="w-5 h-5" />}
            className="text-base px-6 py-3"
          >
            Commencer
          </Button>
          
          <Button
            onClick={handleLearnMore}
            variant="secondary"
            size="lg"
            className="text-base px-6 py-3"
          >
            En Savoir Plus
          </Button>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full mx-auto">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white border border-gray-200 rounded-lg p-6 text-center shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              
              <p className="text-gray-600 text-sm leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Stats */}
        <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl w-full mx-auto">
          {[
            { number: "10K+", label: "Documents Analysés" },
            { number: "50K+", label: "Questions Répondues" },
            { number: "99.9%", label: "Précision IA" },
            { number: "24/7", label: "Disponibilité" }
          ].map((stat, index) => (
            <div
              key={index}
              className="text-center"
            >
              <div className="text-2xl md:text-3xl font-bold text-gray-900 mb-1">
                {stat.number}
              </div>
              <div className="text-gray-600 text-xs md:text-sm">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 