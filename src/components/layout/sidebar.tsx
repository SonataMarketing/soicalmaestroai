"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useAuth } from "@/contexts/auth-context";
import {
  LayoutDashboard,
  Search,
  TrendingUp,
  Wand2,
  Calendar,
  CheckSquare,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Instagram,
  Twitter,
  Facebook,
  Linkedin,
  LogOut,
  User
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Content Scraper", href: "/scraper", icon: Search },
  { name: "Brand Analysis", href: "/brand-analysis", icon: TrendingUp },
  { name: "AI Generator", href: "/generator", icon: Wand2 },
  { name: "Scheduler", href: "/scheduler", icon: Calendar },
  { name: "Review Queue", href: "/review", icon: CheckSquare },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

const socialAccounts = [
  { name: "Instagram", icon: Instagram, status: "connected", count: "12.5K" },
  { name: "Twitter", icon: Twitter, status: "connected", count: "8.2K" },
  { name: "Facebook", icon: Facebook, status: "pending", count: "25.1K" },
  { name: "LinkedIn", icon: Linkedin, status: "connected", count: "5.7K" },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();

  return (
    <div className={cn(
      "flex flex-col h-full bg-white border-r border-gray-200 transition-all duration-300",
      collapsed ? "w-16" : "w-64"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        {!collapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Wand2 className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">SocialMaestro</span>
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="h-8 w-8"
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => (
          <Link key={item.name} href={item.href}>
            <Button
              variant={pathname === item.href ? "default" : "ghost"}
              className={cn(
                "w-full justify-start",
                collapsed && "px-2"
              )}
            >
              <item.icon className="h-4 w-4" />
              {!collapsed && <span className="ml-2">{item.name}</span>}
            </Button>
          </Link>
        ))}
      </nav>

      {/* Social Accounts */}
      {!collapsed && (
        <div className="p-4 border-t">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Connected Accounts</h3>
          <div className="space-y-2">
            {socialAccounts.map((account) => (
              <div key={account.name} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50">
                <div className="flex items-center space-x-2">
                  <account.icon className="h-4 w-4 text-gray-600" />
                  <span className="text-sm text-gray-700">{account.name}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span className="text-xs text-gray-500">{account.count}</span>
                  <div className={cn(
                    "w-2 h-2 rounded-full",
                    account.status === "connected" ? "bg-green-500" : "bg-yellow-500"
                  )} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* User Profile */}
      <div className="p-4 border-t">
        {user ? (
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <Avatar className="h-8 w-8">
                <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${user.full_name}`} alt={user.full_name} />
                <AvatarFallback>
                  {user.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                </AvatarFallback>
              </Avatar>
              {!collapsed && (
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{user.full_name}</p>
                  <p className="text-xs text-gray-500 truncate">{user.email}</p>
                  <p className="text-xs text-blue-600 capitalize font-medium">{user.role}</p>
                </div>
              )}
            </div>
            {!collapsed && (
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start text-gray-600 hover:text-red-600 hover:bg-red-50"
                onClick={logout}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            )}
          </div>
        ) : (
          <div className="flex items-center space-x-3">
            <Avatar className="h-8 w-8">
              <AvatarFallback>
                <User className="h-4 w-4" />
              </AvatarFallback>
            </Avatar>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">Loading...</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
