
import React from 'react';

export const LogoIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M5 5m-2 0a2 2 0 1 0 4 0a2 2 0 1 0-4 0" />
    <path d="M19 5m-2 0a2 2 0 1 0 4 0a2 2 0 1 0-4 0" />
    <path d="M5 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0-4 0" />
    <path d="M19 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0-4 0" />
    <path d="M5 7v10" />
    <path d="M7 5h10" />
    <path d="M19 7v10" />
    <path d="M7 19h10" />
    <path d="M7 7c6 0 6 10 10 10" />
  </svg>
);
