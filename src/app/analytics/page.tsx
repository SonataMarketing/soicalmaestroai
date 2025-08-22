"use client";

import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import {
  TrendingUp,
  TrendingDown,
  Eye,
  Heart,
  MessageCircle,
  Share,
  Users,
  Clock,
  Target,
  BarChart3,
  Download,
  Calendar,
  Instagram,
  Twitter,
  Linkedin,
  Facebook
} from "lucide-react";

const overviewMetrics = [
  {
    title: "Total Reach",
    value: "2.4M",
    change: "+12.5%",
    trend: "up",
    icon: Eye,
    description: "People reached across all platforms"
  },
  {
    title: "Engagement Rate",
    value: "4.8%",
    change: "+0.7%",
    trend: "up",
    icon: Heart,
    description: "Average engagement across all posts"
  },
  {
    title: "Total Followers",
    value: "61.4K",
    change: "+2.3%",
    trend: "up",
    icon: Users,
    description: "Combined followers across platforms"
  },
  {
    title: "Content Published",
    value: "127",
    change: "+18%",
    trend: "up",
    icon: BarChart3,
    description: "Posts published this month"
  }
];

const platformMetrics = [
  {
    platform: "Instagram",
    icon: Instagram,
    color: "text-pink-500",
    followers: "25.1K",
    reach: "1.2M",
    engagement: "5.2%",
    posts: 42,
    topPost: "AI-generated summer fashion trends...",
    growth: "+15%"
  },
  {
    platform: "LinkedIn",
    icon: Linkedin,
    color: "text-blue-600",
    followers: "18.7K",
    reach: "890K",
    engagement: "3.8%",
    posts: 28,
    topPost: "How AI is transforming digital marketing...",
    growth: "+8%"
  },
  {
    platform: "Twitter",
    icon: Twitter,
    color: "text-blue-500",
    followers: "12.3K",
    reach: "456K",
    engagement: "2.9%",
    posts: 67,
    topPost: "Breaking: New AI technology revolutionizes...",
    growth: "+12%"
  },
  {
    platform: "Facebook",
    icon: Facebook,
    color: "text-blue-700",
    followers: "5.3K",
    reach: "234K",
    engagement: "4.1%",
    posts: 19,
    topPost: "Behind the scenes: Our AI development...",
    growth: "+5%"
  }
];

const contentPerformance = [
  {
    type: "Photo Posts",
    count: 78,
    avgEngagement: "5.1%",
    totalReach: "1.8M",
    performance: "excellent",
    trend: "+23%"
  },
  {
    type: "Video Posts",
    count: 34,
    avgEngagement: "7.3%",
    totalReach: "1.1M",
    performance: "excellent",
    trend: "+45%"
  },
  {
    type: "Text Posts",
    count: 15,
    avgEngagement: "2.8%",
    totalReach: "340K",
    performance: "good",
    trend: "-8%"
  }
];

const aiInsights = [
  {
    title: "Best Posting Times",
    insight: "Your audience is most active between 2-4 PM on weekdays",
    recommendation: "Schedule more content during these peak hours",
    impact: "+15% potential engagement increase"
  },
  {
    title: "Content Mix Optimization",
    insight: "Video content performs 3x better than static posts",
    recommendation: "Increase video content to 60% of total posts",
    impact: "+28% potential reach improvement"
  },
  {
    title: "Hashtag Performance",
    insight: "#Innovation and #AI drive highest engagement",
    recommendation: "Use these hashtags in 80% of relevant posts",
    impact: "+12% engagement boost"
  },
  {
    title: "Audience Growth",
    insight: "Educational content drives 2x more followers",
    recommendation: "Create more tutorial and insight-based content",
    impact: "+20% follower growth potential"
  }
];

const topPerformingPosts = [
  {
    id: 1,
    platform: "Instagram",
    type: "video",
    content: "Behind the scenes: How AI analyzes thousands of posts to create content that performs...",
    engagement: {
      likes: 2847,
      comments: 156,
      shares: 89,
      rate: "7.2%"
    },
    reach: 45200,
    date: "Aug 20, 2024"
  },
  {
    id: 2,
    platform: "LinkedIn",
    type: "photo",
    content: "The future of content marketing: AI + Human creativity = Unstoppable results...",
    engagement: {
      likes: 1234,
      comments: 87,
      shares: 156,
      rate: "6.8%"
    },
    reach: 28900,
    date: "Aug 18, 2024"
  },
  {
    id: 3,
    platform: "Twitter",
    type: "photo",
    content: "AI fact: Companies using AI content tools see 340% increase in engagement...",
    engagement: {
      likes: 892,
      comments: 43,
      shares: 127,
      rate: "5.9%"
    },
    reach: 18700,
    date: "Aug 17, 2024"
  }
];

export default function Analytics() {
  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
            <p className="text-gray-600">Track your social media performance and AI insights</p>
          </div>
          <div className="flex space-x-3">
            <Select defaultValue="30days">
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7days">Last 7 days</SelectItem>
                <SelectItem value="30days">Last 30 days</SelectItem>
                <SelectItem value="90days">Last 90 days</SelectItem>
                <SelectItem value="1year">Last year</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
          </div>
        </div>

        {/* Overview Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {overviewMetrics.map((metric) => (
            <Card key={metric.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  {metric.title}
                </CardTitle>
                <metric.icon className="h-4 w-4 text-gray-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
                <div className="flex items-center space-x-1 mt-1">
                  {metric.trend === "up" ? (
                    <TrendingUp className="h-3 w-3 text-green-600" />
                  ) : (
                    <TrendingDown className="h-3 w-3 text-red-600" />
                  )}
                  <span className={`text-xs ${
                    metric.trend === "up" ? "text-green-600" : "text-red-600"
                  }`}>
                    {metric.change}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{metric.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="platforms">Platform Analysis</TabsTrigger>
            <TabsTrigger value="content">Content Performance</TabsTrigger>
            <TabsTrigger value="ai-insights">AI Insights</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Top Performing Posts */}
              <Card>
                <CardHeader>
                  <CardTitle>Top Performing Posts</CardTitle>
                  <CardDescription>Your most successful content this month</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {topPerformingPosts.map((post) => (
                    <div key={post.id} className="p-4 border rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        {post.platform === "Instagram" && <Instagram className="h-4 w-4 text-pink-500" />}
                        {post.platform === "LinkedIn" && <Linkedin className="h-4 w-4 text-blue-600" />}
                        {post.platform === "Twitter" && <Twitter className="h-4 w-4 text-blue-500" />}
                        <span className="text-sm font-medium">{post.platform}</span>
                        <Badge variant={post.type === "video" ? "default" : "secondary"}>
                          {post.type}
                        </Badge>
                        <span className="text-xs text-gray-500">{post.date}</span>
                      </div>
                      <p className="text-sm text-gray-700 mb-3">{post.content}</p>
                      <div className="grid grid-cols-4 gap-4 text-xs text-gray-500">
                        <div className="text-center">
                          <div className="font-medium text-gray-900">{post.engagement.likes}</div>
                          <div>Likes</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-900">{post.engagement.comments}</div>
                          <div>Comments</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-900">{post.engagement.shares}</div>
                          <div>Shares</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-900">{post.engagement.rate}</div>
                          <div>Rate</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Growth Trends */}
              <Card>
                <CardHeader>
                  <CardTitle>Growth Trends</CardTitle>
                  <CardDescription>Monthly performance comparison</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium">Follower Growth</span>
                        <span className="text-sm text-green-600">+12.3%</span>
                      </div>
                      <Progress value={76} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium">Engagement Rate</span>
                        <span className="text-sm text-green-600">+8.7%</span>
                      </div>
                      <Progress value={63} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium">Content Output</span>
                        <span className="text-sm text-green-600">+23.1%</span>
                      </div>
                      <Progress value={89} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium">Brand Consistency</span>
                        <span className="text-sm text-green-600">+5.2%</span>
                      </div>
                      <Progress value={94} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="platforms" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {platformMetrics.map((platform) => (
                <Card key={platform.platform}>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <platform.icon className={`h-5 w-5 ${platform.color}`} />
                      <span>{platform.platform}</span>
                      <Badge variant="outline" className="ml-auto">
                        {platform.growth}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <div className="text-2xl font-bold">{platform.followers}</div>
                        <div className="text-sm text-gray-500">Followers</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold">{platform.reach}</div>
                        <div className="text-sm text-gray-500">Monthly Reach</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold">{platform.engagement}</div>
                        <div className="text-sm text-gray-500">Avg Engagement</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold">{platform.posts}</div>
                        <div className="text-sm text-gray-500">Posts This Month</div>
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-sm font-medium mb-1">Top Post</div>
                      <div className="text-sm text-gray-600">{platform.topPost}</div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="content" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Content Type Performance</CardTitle>
                <CardDescription>How different content types are performing</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {contentPerformance.map((content) => (
                    <div key={content.type} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium">{content.type}</h4>
                        <div className="flex items-center space-x-2">
                          <Badge variant={
                            content.performance === "excellent" ? "default" :
                            content.performance === "good" ? "secondary" : "destructive"
                          }>
                            {content.performance}
                          </Badge>
                          <span className={`text-sm ${
                            content.trend.startsWith("+") ? "text-green-600" : "text-red-600"
                          }`}>
                            {content.trend}
                          </span>
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <div className="font-medium text-gray-900">{content.count}</div>
                          <div className="text-gray-500">Posts Published</div>
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{content.avgEngagement}</div>
                          <div className="text-gray-500">Avg Engagement</div>
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{content.totalReach}</div>
                          <div className="text-gray-500">Total Reach</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ai-insights" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>AI-Generated Insights</CardTitle>
                <CardDescription>Intelligent recommendations to improve your social media performance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {aiInsights.map((insight, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">{insight.title}</h4>
                      <p className="text-sm text-gray-600 mb-2">{insight.insight}</p>
                      <div className="p-3 bg-blue-50 rounded border-l-4 border-blue-500 mb-2">
                        <p className="text-sm text-blue-800">{insight.recommendation}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Target className="h-4 w-4 text-green-600" />
                        <span className="text-sm font-medium text-green-600">{insight.impact}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* AI Performance Summary */}
        <Card>
          <CardHeader>
            <CardTitle>AI Assistant Performance</CardTitle>
            <CardDescription>How AI is improving your social media management</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">89%</div>
                <div className="text-sm text-gray-500">Content Approval Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">3.2x</div>
                <div className="text-sm text-gray-500">Faster Content Creation</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">+34%</div>
                <div className="text-sm text-gray-500">Engagement Improvement</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">15hrs</div>
                <div className="text-sm text-gray-500">Time Saved Weekly</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
