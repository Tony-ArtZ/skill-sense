"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, Users, Award, BarChart3, Loader2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

interface AnalyticsData {
  totalEmployees: number;
  totalSkills: number;
  avgConfidence: number;
  skillsDistribution: Array<{ category: string; count: number }>;
  topSkills: Array<{ skill: string; count: number; avgConfidence: number }>;
  departmentStats: Array<{
    department: string;
    employeeCount: number;
    avgSkills: number;
  }>;
}

const COLORS = [
  "#58a6ff",
  "#79c0ff",
  "#a5d6ff",
  "#388bfd",
  "#1f6feb",
  "#0969da",
];

export default function AnalyticsDashboard() {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const [employeesRes, skillsRes, distributionRes] = await Promise.all([
        fetch("http://localhost:8001/employees"),
        fetch("http://localhost:8001/skills"),
        fetch("http://localhost:8001/analytics/skills-distribution"),
      ]);

      const [employees, skills, distribution] = await Promise.all([
        employeesRes.json(),
        skillsRes.json(),
        distributionRes.json(),
      ]);

      // Process data for category distribution (group by category)
      const categoryMap = new Map<string, number>();
      distribution.data?.forEach((item: any) => {
        const category = item.category || "Other";
        const count = categoryMap.get(category) || 0;
        categoryMap.set(category, count + (item.employee_count || 0));
      });

      const skillsDistribution = Array.from(categoryMap.entries()).map(
        ([category, count]) => ({
          category,
          count,
        })
      );

      // Get top skills sorted by employee count
      const topSkills =
        distribution.data
          ?.sort(
            (a: any, b: any) =>
              (b.employee_count || 0) - (a.employee_count || 0)
          )
          .slice(0, 10)
          .map((skill: any) => ({
            skill: skill.skill_name || "Unknown",
            count: skill.employee_count || 0,
            avgConfidence: Math.round((skill.avg_proficiency || 0) * 100),
          })) || [];

      // Calculate average confidence from all skills
      const totalConfidence =
        distribution.data?.reduce(
          (sum: number, item: any) => sum + (item.avg_proficiency || 0),
          0
        ) || 0;
      const avgConfidence = distribution.data?.length
        ? (totalConfidence / distribution.data.length) * 100
        : 0;

      setAnalytics({
        totalEmployees: employees.data?.length || 0,
        totalSkills: skills.data?.length || 0,
        avgConfidence,
        skillsDistribution,
        topSkills,
        departmentStats: [],
      });
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Failed to load analytics data.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Stats Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <Card className="border border-primary/30 bg-card shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground font-mono uppercase tracking-wider">
              profiles
            </CardTitle>
            <Users className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground font-mono">
              {analytics.totalEmployees}
            </div>
            <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1 font-mono">
              <span className="text-primary">›</span>talent_graph_nodes
            </p>
          </CardContent>
        </Card>

        <Card className="border border-primary/30 bg-card shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground font-mono uppercase tracking-wider">
              skills
            </CardTitle>
            <Award className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground font-mono">
              {analytics.totalSkills}
            </div>
            <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1 font-mono">
              <span className="text-primary">›</span>unique_extracted
            </p>
          </CardContent>
        </Card>

        <Card className="border border-primary/30 bg-card shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground font-mono uppercase tracking-wider">
              confidence
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground font-mono">
              {analytics.avgConfidence.toFixed(0)}%
            </div>
            <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1 font-mono">
              <span className="text-primary">›</span>avg_validation
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Skills Distribution Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="border border-border bg-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground font-mono text-sm">
              <span className="text-primary">$</span>
              analyze --type=distribution
            </CardTitle>
            <CardDescription className="font-mono text-xs">
              capability_map • category_breakdown • coverage_analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analytics.skillsDistribution.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analytics.skillsDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d1f4a" />
                  <XAxis dataKey="category" stroke="#9b87f5" />
                  <YAxis stroke="#9b87f5" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#13091f",
                      border: "1px solid #2d1f4a",
                      borderRadius: "8px",
                      color: "#e8e4f0",
                    }}
                  />
                  <Bar dataKey="count" fill="#9b87f5" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                No skills data available yet
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Top Skills */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="border border-border bg-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground font-mono text-sm">
              <span className="text-primary">$</span>
              query --top-skills --limit=8
            </CardTitle>
            <CardDescription className="font-mono text-xs">
              frequency_ranked • confidence_weighted • prevalence_metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.topSkills.slice(0, 8).map((skill, idx) => (
                <motion.div
                  key={skill.skill}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + idx * 0.05 }}
                  className="space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Badge
                        variant="secondary"
                        className="text-xs bg-background text-muted-foreground border border-border font-mono"
                      >
                        {idx + 1}
                      </Badge>
                      <span className="font-medium text-foreground font-mono text-sm">
                        {skill.skill}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-muted-foreground font-mono">
                        count={skill.count}
                      </span>
                      <span className="text-sm font-semibold text-primary font-mono">
                        {skill.avgConfidence}%
                      </span>
                    </div>
                  </div>
                  <Progress value={skill.avgConfidence} className="h-2" />
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Skills Category Pie Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="border border-border bg-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground font-mono text-sm">
              <span className="text-primary">$</span>
              visualize --type=pie --data=categories
            </CardTitle>
            <CardDescription className="font-mono text-xs">
              category_breakdown • percentage_distribution
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analytics.skillsDistribution.length > 0 ? (
              <div className="flex items-center justify-center">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analytics.skillsDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry: any) =>
                        `${entry.category}: ${(
                          (entry.percent || 0) * 100
                        ).toFixed(0)}%`
                      }
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {analytics.skillsDistribution.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#13091f",
                        border: "1px solid #2d1f4a",
                        borderRadius: "8px",
                        color: "#e8e4f0",
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[300px] flex items-center justify-center text-purple-600">
                No category data available yet
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
