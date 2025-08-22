"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import {
  Search,
  TrendingUp,
  Heart,
  MessageCircle,
  Share,
  Clock,
  Filter,
  Download,
  Plus,
  RefreshCw,
  Instagram,
  Globe
} from "lucide-react";

const trendingTopics = [
  { keyword: "#AIContent", posts: 1247, engagement: "High", platform: "Instagram" },
  { keyword: "#SocialMarketing", posts: 892, engagement: "Medium", platform: "Reddit" },
  { keyword: "#DigitalTrends", posts: 2156, engagement: "High", platform: "Instagram" },
  { keyword: "#BrandStrategy", posts: 634, engagement: "Medium", platform: "Reddit" },
  { keyword: "#ContentCreation", posts: 1893, engagement: "High", platform: "Instagram" },
];

const scrapedContent = [
  {
    id: 1,
    platform: "Instagram",
    author: "@trendsetter_ai",
    content: "The future of AI in social media is here! 🚀 Brands are using machine learning to create personalized content that resonates with their audience. What do you think about AI-generated posts?",
    engagement: { likes: 2847, comments: 156, shares: 89 },
    hashtags: ["#AI", "#SocialMedia", "#Marketing", "#Innovation"],
    timestamp: "2 hours ago",
    relevanceScore: 94,
    imageUrl: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=400&fit=crop"
  },
  {
    id: 2,
    platform: "Reddit",
    author: "u/marketing_guru",
    subreddit: "r/socialmedia",
    content: "Discussion: How are you measuring the ROI of AI-generated content? Our agency has seen a 340% increase in engagement since implementing AI tools for content creation. Here are the key metrics we track...",
    engagement: { likes: 187, comments: 43, shares: 12 },
    timestamp: "4 hours ago",
    relevanceScore: 87,
  },
  {
    id: 3,
    platform: "Instagram",
    author: "@digitalmarketer",
    content: "Brand consistency is everything! 💡 Here's how we maintain our voice across all platforms while using AI to scale our content production. Swipe for tips ➡️",
    engagement: { likes: 1456, comments: 78, shares: 34 },
    hashtags: ["#BrandStrategy", "#ContentMarketing", "#AI"],
    timestamp: "6 hours ago",
    relevanceScore: 91,
    imageUrl: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=400&fit=crop"
  }
];

export default function ContentScraper() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPlatform, setSelectedPlatform] = useState("all");
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async () => {
    setIsSearching(true);
    // Simulate API call
    setTimeout(() => setIsSearching(false), 2000);
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Content Scraper</h1>
            <p className="text-gray-600">Discover trending content from Instagram and Reddit</p>
          </div>
          <Button>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Data
          </Button>
        </div>

        {/* Search Controls */}
        <Card>
          <CardHeader>
            <CardTitle>Search & Filter</CardTitle>
            <CardDescription>Find content that resonates with your audience</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex space-x-4">
              <div className="flex-1">
                <Input
                  placeholder="Search keywords, hashtags, or topics..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full"
                />
              </div>
              <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Platform" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Platforms</SelectItem>
                  <SelectItem value="instagram">Instagram</SelectItem>
                  <SelectItem value="reddit">Reddit</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={handleSearch} disabled={isSearching}>
                {isSearching ? (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Search className="h-4 w-4 mr-2" />
                )}
                Search
              </Button>
            </div>

            <div className="flex items-center space-x-4">
              <Badge variant="secondary">
                <Filter className="h-3 w-3 mr-1" />
                High Engagement
              </Badge>
              <Badge variant="secondary">Last 24h</Badge>
              <Badge variant="secondary">Trending Up</Badge>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Trending Topics Sidebar */}
          <Card>
            <CardHeader>
              <CardTitle>Trending Topics</CardTitle>
              <CardDescription>Hot topics right now</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {trendingTopics.map((topic, index) => (
                <div key={index} className="p-3 rounded-lg border hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{topic.keyword}</span>
                    {topic.platform === "Instagram" ? (
                      <Instagram className="h-4 w-4 text-pink-500" />
                    ) : (
                      <Globe className="h-4 w-4 text-orange-500" />
                    )}
                  </div>
                  <div className="text-xs text-gray-500">
                    {topic.posts} posts
                  </div>
                  <Badge
                    variant={topic.engagement === "High" ? "default" : "secondary"}
                    className="text-xs mt-1"
                  >
                    {topic.engagement} engagement
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Content Feed */}
          <div className="lg:col-span-3">
            <Tabs defaultValue="discovered" className="space-y-4">
              <TabsList>
                <TabsTrigger value="discovered">Discovered Content</TabsTrigger>
                <TabsTrigger value="saved">Saved for Later</TabsTrigger>
                <TabsTrigger value="analytics">Analytics</TabsTrigger>
              </TabsList>

              <TabsContent value="discovered" className="space-y-4">
                {scrapedContent.map((item) => (
                  <Card key={item.id}>
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <Badge variant={item.platform === "Instagram" ? "default" : "secondary"}>
                            {item.platform === "Instagram" ? (
                              <Instagram className="h-3 w-3 mr-1" />
                            ) : (
                              <Globe className="h-3 w-3 mr-1" />
                            )}
                            {item.platform}
                          </Badge>
                          <span className="text-sm font-medium">{item.author}</span>
                          {item.platform === "Reddit" && (
                            <span className="text-sm text-gray-500">{item.subreddit}</span>
                          )}
                          <span className="text-sm text-gray-500">{item.timestamp}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="text-xs">
                            {item.relevanceScore}% relevant
                          </Badge>
                          <Button variant="ghost" size="sm">
                            <Plus className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        {item.imageUrl && (
                          <div className="md:col-span-1">
                            <img
                              src={item.imageUrl}
                              alt="Content preview"
                              className="w-full h-32 object-cover rounded-lg"
                            />
                          </div>
                        )}
                        <div className={item.imageUrl ? "md:col-span-3" : "md:col-span-4"}>
                          <p className="text-gray-700 mb-3">{item.content}</p>

                          {item.hashtags && (
                            <div className="flex flex-wrap gap-1 mb-3">
                              {item.hashtags.map((hashtag, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {hashtag}
                                </Badge>
                              ))}
                            </div>
                          )}

                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4 text-sm text-gray-500">
                              <div className="flex items-center space-x-1">
                                <Heart className="h-4 w-4" />
                                <span>{item.engagement.likes}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <MessageCircle className="h-4 w-4" />
                                <span>{item.engagement.comments}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Share className="h-4 w-4" />
                                <span>{item.engagement.shares}</span>
                              </div>
                            </div>
                            <div className="flex space-x-2">
                              <Button variant="outline" size="sm">
                                <Download className="h-4 w-4 mr-1" />
                                Save
                              </Button>
                              <Button size="sm">
                                Inspire Content
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>

              <TabsContent value="saved">
                <Card>
                  <CardContent className="p-6 text-center">
                    <p className="text-gray-500">No saved content yet. Start discovering and saving content to build your inspiration library.</p>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="analytics">
                <Card>
                  <CardHeader>
                    <CardTitle>Scraping Analytics</CardTitle>
                    <CardDescription>Performance metrics for content discovery</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900">2,847</div>
                        <div className="text-sm text-gray-500">Posts Analyzed</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900">127</div>
                        <div className="text-sm text-gray-500">High-Value Content</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900">23</div>
                        <div className="text-sm text-gray-500">Content Ideas Generated</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
