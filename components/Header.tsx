
import React from 'react';
import { LogoIcon } from './icons/LogoIcon';

const Header: React.FC = () => {
  return (
    <header className="py-6">
      <div className="flex items-center justify-center">
        <a href="/" className="flex items-center gap-3 group">
          <LogoIcon className="w-8 h-8 text-green-500 group-hover:text-green-400 transition-colors duration-300" />
          <span className="text-2xl font-bold tracking-tighter text-gray-200 group-hover:text-white transition-colors duration-300">
            vectorizer.dev
          </span>
        </a>
      </div>
    </header>
  );
};

export default Header;
