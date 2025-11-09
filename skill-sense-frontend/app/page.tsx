"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Sparkles,
  Search,
  Upload,
  Users,
  TrendingUp,
  Brain,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import IngestionPage from "@/components/ingestion-page";
import QueryDashboard from "@/components/query-dashboard";
import AnalyticsDashboard from "@/components/analytics-dashboard";

export default function Home() {
  const [activeTab, setActiveTab] = useState("query");

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        {/* Gradient Background */}
        <div className="absolute inset-0 bg-linear-to-br from-background via-purple-950/20 to-background" />

        {/* Animated Blobs */}
        <div className="absolute top-0 -left-4 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob" />
        <div className="absolute top-0 -right-4 w-96 h-96 bg-violet-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000" />
        <div className="absolute -bottom-8 left-20 w-96 h-96 bg-purple-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000" />

        {/* Grid Pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#2d1f4a_1px,transparent_1px),linear-gradient(to_bottom,#2d1f4a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)] opacity-30" />

        {/* Floating Particles */}
        <div className="absolute inset-0">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-primary/30 rounded-full animate-float"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${3 + Math.random() * 4}s`,
              }}
            />
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-b border-border bg-card/80 backdrop-blur-xl sticky top-0 z-50 shadow-lg shadow-primary/5"
        >
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <motion.div
                className="flex items-center gap-3"
                whileHover={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 400 }}
              >
                <div className="w-12 h-12 bg-linear-to-br from-primary to-purple-600 rounded-xl flex items-center justify-center shadow-md shadow-primary/20">
                  <Brain className="w-7 h-7 text-primary-foreground" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-linear-to-r from-primary via-purple-400 to-primary bg-clip-text text-transparent">
                    SkillSense
                  </h1>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-primary animate-pulse" />
                    Talent Intelligence System
                  </p>
                </div>
              </motion.div>
              <nav className="flex items-center gap-2">
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    variant={activeTab === "query" ? "secondary" : "ghost"}
                    size="sm"
                    onClick={() => setActiveTab("query")}
                    className={
                      activeTab === "query"
                        ? "bg-primary/20 border border-primary/30 shadow-lg shadow-primary/20"
                        : ""
                    }
                  >
                    <Search className="mr-2 h-4 w-4" />
                    Query
                  </Button>
                </motion.div>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    variant={activeTab === "ingest" ? "secondary" : "ghost"}
                    size="sm"
                    onClick={() => setActiveTab("ingest")}
                    className={
                      activeTab === "ingest"
                        ? "bg-primary/20 border border-primary/30 shadow-lg shadow-primary/20"
                        : ""
                    }
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    Ingest
                  </Button>
                </motion.div>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    variant={activeTab === "analytics" ? "secondary" : "ghost"}
                    size="sm"
                    onClick={() => setActiveTab("analytics")}
                    className={
                      activeTab === "analytics"
                        ? "bg-primary/20 border border-primary/30 shadow-lg shadow-primary/20"
                        : ""
                    }
                  >
                    <TrendingUp className="mr-2 h-4 w-4" />
                    Analytics
                  </Button>
                </motion.div>
              </nav>
            </div>
          </div>
        </motion.header>

        {/* Hero Section */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="py-12 px-4"
        >
          <div className="container mx-auto text-center max-w-4xl">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="mb-6"
            >
              <motion.div
                className="inline-block mb-6 px-6 py-3 border-2 border-primary/40 rounded-xl bg-linear-to-r from-primary/10 via-purple-500/10 to-primary/10 backdrop-blur-sm shadow-md shadow-primary/10"
                animate={{
                  boxShadow: [
                    "0 0 10px rgba(155, 135, 245, 0.15)",
                    "0 0 15px rgba(155, 135, 245, 0.25)",
                    "0 0 10px rgba(155, 135, 245, 0.15)",
                  ],
                }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <span className="text-primary font-semibold text-sm flex items-center gap-2">
                  <Sparkles className="w-4 h-4 animate-pulse" />
                  Enterprise Talent Intelligence Platform
                </span>
              </motion.div>
              <h2 className="text-6xl font-bold mb-6 bg-linear-to-r from-primary via-purple-400 to-violet-400 bg-clip-text text-transparent animate-shimmer">
                Query Your Talent Graph
              </h2>
              <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
                Natural language queries across multimodal data sources. Extract
                hidden skills, identify gaps, and assemble optimal teams with
                evidence-backed insights.
              </p>
            </motion.div>

            {/* Feature Pills */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="flex flex-wrap justify-center gap-3 mb-8"
            >
              <motion.div
                className="px-5 py-2.5 rounded-xl border-2 border-primary/30 bg-card/95 shadow-md shadow-primary/5 hover:shadow-lg hover:shadow-primary/15 transition-all group"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <span className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Upload className="w-4 h-4 text-primary group-hover:animate-pulse" />
                  Multimodal Ingest
                </span>
              </motion.div>
              <motion.div
                className="px-5 py-2.5 rounded-xl border-2 border-primary/30 bg-card/95 shadow-md shadow-primary/5 hover:shadow-lg hover:shadow-primary/15 transition-all group"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <span className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Search className="w-4 h-4 text-primary group-hover:animate-pulse" />
                  NL-to-SQL
                </span>
              </motion.div>
              <motion.div
                className="px-5 py-2.5 rounded-xl border-2 border-primary/30 bg-card/95 shadow-md shadow-primary/5 hover:shadow-lg hover:shadow-primary/15 transition-all group"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <span className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Brain className="w-4 h-4 text-primary group-hover:animate-pulse" />
                  RAG Search
                </span>
              </motion.div>
              <motion.div
                className="px-5 py-2.5 rounded-xl border-2 border-primary/30 bg-card/95 shadow-md shadow-primary/5 hover:shadow-lg hover:shadow-primary/15 transition-all group"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <span className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-primary group-hover:animate-pulse" />
                  Gap Analysis
                </span>
              </motion.div>
            </motion.div>
          </div>
        </motion.section>

        {/* Main Content */}
        <div className="container mx-auto px-4 pb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="w-full"
            >
              <TabsList className="grid w-full max-w-2xl mx-auto grid-cols-3 mb-8 bg-card/80 backdrop-blur-xl border-2 border-border shadow-xl shadow-primary/10 p-2 rounded-2xl h-14">
                <TabsTrigger
                  value="query"
                  className="flex items-center justify-center gap-2 data-[state=active]:bg-linear-to-br data-[state=active]:from-primary/20 data-[state=active]:to-purple-500/20 data-[state=active]:text-primary data-[state=active]:shadow-lg data-[state=active]:shadow-primary/25 rounded-xl transition-all duration-300 font-semibold text-sm h-full"
                >
                  <Search className="w-4 h-4" />
                  Query
                </TabsTrigger>
                <TabsTrigger
                  value="ingest"
                  className="flex items-center justify-center gap-2 data-[state=active]:bg-linear-to-br data-[state=active]:from-primary/20 data-[state=active]:to-purple-500/20 data-[state=active]:text-primary data-[state=active]:shadow-lg data-[state=active]:shadow-primary/25 rounded-xl transition-all duration-300 font-semibold text-sm h-full"
                >
                  <Upload className="w-4 h-4" />
                  Ingest
                </TabsTrigger>
                <TabsTrigger
                  value="analytics"
                  className="flex items-center justify-center gap-2 data-[state=active]:bg-linear-to-br data-[state=active]:from-primary/20 data-[state=active]:to-purple-500/20 data-[state=active]:text-primary data-[state=active]:shadow-lg data-[state=active]:shadow-primary/25 rounded-xl transition-all duration-300 font-semibold text-sm h-full"
                >
                  <TrendingUp className="w-4 h-4" />
                  Analytics
                </TabsTrigger>
              </TabsList>

              <TabsContent value="query" className="mt-0">
                <QueryDashboard />
              </TabsContent>

              <TabsContent value="ingest" className="mt-0">
                <IngestionPage />
              </TabsContent>

              <TabsContent value="analytics" className="mt-0">
                <AnalyticsDashboard />
              </TabsContent>
            </Tabs>
          </motion.div>
        </div>

        {/* Footer */}
        <footer className="border-t border-border/50 bg-card/50 backdrop-blur-lg mt-12">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <div className="flex items-center gap-2 font-mono">
                <span className="text-primary">›</span>
                <p>SkillSense v1.0.0</p>
              </div>
              <div className="flex gap-6 font-mono text-xs">
                <a
                  href="#"
                  className="hover:text-primary transition-colors flex items-center gap-1"
                >
                  <span className="text-primary">$</span>docs
                </a>
                <a
                  href="#"
                  className="hover:text-primary transition-colors flex items-center gap-1"
                >
                  <span className="text-primary">$</span>api
                </a>
                <a
                  href="#"
                  className="hover:text-primary transition-colors flex items-center gap-1"
                >
                  <span className="text-primary">$</span>github
                </a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
