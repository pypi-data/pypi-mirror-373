'use client';

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { User, LogOut, Settings, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface UserDropdownProps {
  user: {
    username: string;
    avatar_url?: string;
    email?: string;
  } | null;
  onLogout: () => void;
}

export function UserDropdown({ user, onLogout }: UserDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!user) return null;

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 px-2 py-1 rounded-md transition-all",
          "hover:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-ring",
          isOpen && "bg-muted/50"
        )}
      >
        {user.avatar_url ? (
          <Image 
            src={user.avatar_url} 
            alt={user.username} 
            width={24} 
            height={24} 
            className="rounded-full border border-border"
          />
        ) : (
          <div className="w-6 h-6 rounded-full bg-muted border border-border flex items-center justify-center">
            <User className="w-4 h-4 text-muted-foreground" />
          </div>
        )}
        <span className="text-sm text-muted-foreground hidden sm:inline">
          {user.username}
        </span>
        <ChevronDown className={cn(
          "w-3 h-3 text-muted-foreground transition-transform",
          isOpen && "rotate-180"
        )} />
      </button>

      {isOpen && (
        <div className={cn(
          "absolute right-0 mt-2 w-48 py-1",
          "bg-background border border-border rounded-md shadow-lg",
          "z-50 animate-in fade-in-0 zoom-in-95 slide-in-from-top-2",
          "terminal-glow"
        )}>
          <div className="px-3 py-2 border-b border-border">
            <p className="text-sm font-medium">{user.username}</p>
            {user.email && (
              <p className="text-xs text-muted-foreground truncate">{user.email}</p>
            )}
          </div>
          
          <button
            onClick={() => {
              // Settings action placeholder
              setIsOpen(false);
            }}
            className={cn(
              "w-full px-3 py-2 text-left text-sm",
              "hover:bg-muted/50 transition-colors",
              "flex items-center gap-2"
            )}
          >
            <Settings className="w-4 h-4" />
            Settings
          </button>
          
          <div className="border-t border-border">
            <button
              onClick={() => {
                onLogout();
                setIsOpen(false);
              }}
              className={cn(
                "w-full px-3 py-2 text-left text-sm",
                "hover:bg-muted/50 transition-colors",
                "flex items-center gap-2 text-destructive"
              )}
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
}