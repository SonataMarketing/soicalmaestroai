"use client";

import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  TrendingUp,
  Users,
  Calendar,
  CheckCircle,
  AlertCircle,
  Eye,
  Heart,
  Share,
  MessageCircle,
  Clock,
  Zap
} from "lucide-react";

const metrics = [
  {
    title: "Total Reach",
    value: "2.4M",
    change: "+12.5%",
    icon: Eye,
    trend: "up"
  },
  {
    title: "Engagement Rate",
    value: "4.8%",
    change: "+0.7%",
    icon: Heart,
    trend: "up"
  },
  {
    title: "Scheduled Posts",
    value: "28",
    change: "Today",
    icon: Calendar,
    trend: "neutral"
  },
  {
    title: "Pending Reviews",
    value: "12",
    change: "Requires action",
    icon: AlertCircle,
    trend: "warning"
  }
];

const recentPosts = [
  {
    id: 1,
    platform: "Instagram",
    content: "AI-generated summer fashion trends that are taking over social media...",
    status: "published",
    engagement: { likes: 324, comments: 48, shares: 12 },
    time: "2 hours ago"
  },
  {
    id: 2,
    platform: "Twitter",
    content: "Breaking: New AI technology revolutionizes content creation for brands...",
    status: "scheduled",
    engagement: { likes: 0, comments: 0, shares: 0 },
    time: "In 3 hours"
  },
  {
    id: 3,
    platform: "LinkedIn",
    content: "How AI is transforming digital marketing strategies in 2024...",
    status: "review",
    engagement: { likes: 0, comments: 0, shares: 0 },
    time: "Pending review"
  }
];

const brandInsights = [
  { metric: "Brand Voice Consistency", score: 92, color: "bg-green-500" },
  { metric: "Content Relevance", score: 88, color: "bg-blue-500" },
  { metric: "Audience Alignment", score: 76, color: "bg-yellow-500" },
  { metric: "Trend Adoption", score: 84, color: "bg-purple-500" }
];

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600">Welcome back! Here's your social media overview.</p>
          </div>
          <div className="flex space-x-3">
            <Button variant="outline">
              <Zap className="h-4 w-4 mr-2" />
              Generate Content
            </Button>
            <Button>
              <Calendar className="h-4 w-4 mr-2" />
              Schedule Post
            </Button>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric) => (
            <Card key={metric.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  {metric.title}
                </CardTitle>
                <metric.icon className="h-4 w-4 text-gray-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
                <p className={`text-xs ${
                  metric.trend === "up" ? "text-green-600" :
                  metric.trend === "warning" ? "text-amber-600" : "text-gray-600"
                }`}>
                  {metric.change}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Posts */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Recent Posts</CardTitle>
              <CardDescription>Latest content across all platforms</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentPosts.map((post) => (
                <div key={post.id} className="flex items-start space-x-4 p-4 rounded-lg border">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <Badge variant="secondary">{post.platform}</Badge>
                      <Badge variant={
                        post.status === "published" ? "default" :
                        post.status === "scheduled" ? "secondary" : "destructive"
                      }>
                        {post.status}
                      </Badge>
                      <span className="text-sm text-gray-500">{post.time}</span>
                    </div>
                    <p className="text-sm text-gray-700 mb-3">{post.content}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <Heart className="h-3 w-3" />
                        <span>{post.engagement.likes}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <MessageCircle className="h-3 w-3" />
                        <span>{post.engagement.comments}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Share className="h-3 w-3" />
                        <span>{post.engagement.shares}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Brand Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Brand Health</CardTitle>
              <CardDescription>AI analysis of your brand performance</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {brandInsights.map((insight) => (
                <div key={insight.metric} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">{insight.metric}</span>
                    <span className="font-medium">{insight.score}%</span>
                  </div>
                  <Progress value={insight.score} className="h-2" />
                </div>
              ))}
              <Separator className="my-4" />
              <Button variant="outline" className="w-full">
                <TrendingUp className="h-4 w-4 mr-2" />
                View Full Analysis
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and workflows</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <Eye className="h-6 w-6" />
                <span>Scrape Trending Content</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <Zap className="h-6 w-6" />
                <span>Generate Post Ideas</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <CheckCircle className="h-6 w-6" />
                <span>Review Pending Content</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
    </ProtectedRoute>
  );
}
