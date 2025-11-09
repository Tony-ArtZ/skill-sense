"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Search,
  Loader2,
  Sparkles,
  Users,
  Award,
  TrendingUp,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

interface QueryResult {
  success: boolean;
  answer: string;
  sql_query?: string;
  results?: any[];
  query_type?: string;
  processing_time_ms?: number;
  error?: string;
}

export default function QueryDashboard() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);

  const exampleQueries = [
    "Who are the best candidates to lead Project Phoenix?",
    "Does Alice's resume show experience with Python and leadership?",
    "Compare Alice's skills from her resume with Bob's skills from his performance review",
    "Show me all engineers with less than 2 years of experience who know React",
    "Generate a final team proposal for Project Phoenix with justifications",
  ];

  const handleQuery = async (queryText: string) => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8001/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: queryText }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        success: false,
        answer: "",
        error:
          "Failed to connect to the API server. Make sure it's running on port 8001.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      handleQuery(query);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        <Card className="border-2 border-primary/30 shadow-xl shadow-primary/10 bg-card/95 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-3 text-foreground text-lg">
              <div className="w-10 h-10 bg-linear-to-br from-primary to-purple-600 rounded-xl flex items-center justify-center shadow-md shadow-primary/20">
                <Search className="w-5 h-5 text-primary-foreground" />
              </div>
              Natural Language Query Interface
            </CardTitle>
            <CardDescription className="text-sm">
              Query structured data and document content using natural language
              • Hybrid NL-to-SQL + RAG system
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex gap-3">
                <div className="flex-1 flex items-center gap-3 bg-background/50 border-2 border-primary/30 rounded-xl px-4 h-14 focus-within:border-primary focus-within:shadow-md focus-within:shadow-primary/15 transition-all backdrop-blur-sm">
                  <Sparkles className="w-5 h-5 text-primary animate-pulse" />
                  <Input
                    placeholder="e.g., Who are our top 3 experts in Docker with leadership skills?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-base h-full placeholder:text-muted-foreground/60"
                    disabled={loading}
                  />
                </div>
                <Button
                  type="submit"
                  size="lg"
                  disabled={loading || !query.trim()}
                  className="px-10 h-14 bg-linear-to-r from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90 shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/30 transition-all duration-300 text-primary-foreground font-semibold text-base rounded-xl"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Searching
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-5 w-5" />
                      Search
                    </>
                  )}
                </Button>
              </div>
            </form>

            {/* Example Queries */}
            <div className="mt-6">
              <p className="text-sm text-muted-foreground mb-3 flex items-center gap-2 font-semibold">
                <Sparkles className="w-4 h-4 text-primary" />
                Example queries:
              </p>
              <div className="flex flex-wrap gap-2">
                {exampleQueries.map((example, idx) => (
                  <motion.button
                    key={idx}
                    whileHover={{ scale: 1.02, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => {
                      setQuery(example);
                      handleQuery(example);
                    }}
                    className="px-4 py-2 text-sm rounded-lg bg-primary/10 text-foreground hover:bg-primary/20 hover:shadow-md hover:shadow-primary/10 transition-all border border-primary/30"
                  >
                    {example}
                  </motion.button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-4xl mx-auto space-y-4"
        >
          {result.success ? (
            <>
              {/* Query Metadata */}
              <Card className="border border-primary/20 bg-card/50 shadow-sm">
                <CardContent className="pt-4">
                  <div className="flex items-center gap-4 text-xs font-mono">
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">query_type:</span>
                      <Badge
                        variant="outline"
                        className={`font-mono ${
                          result.query_type === "HYBRID" ||
                          result.query_type === "ADVANCED_HYBRID"
                            ? "border-purple-500/50 text-purple-400"
                            : result.query_type === "RAG"
                            ? "border-blue-500/50 text-blue-400"
                            : "border-green-500/50 text-green-400"
                        }`}
                      >
                        {result.query_type || "HYBRID"}
                      </Badge>
                    </div>
                    {result.processing_time_ms && (
                      <div className="flex items-center gap-2">
                        <span className="text-muted-foreground">
                          processing_time:
                        </span>
                        <span className="text-primary">
                          {result.processing_time_ms}ms
                        </span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Answer Summary */}
              <Card className="border border-primary/30 bg-card shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-foreground font-mono text-sm">
                    <span className="text-primary">$</span>
                    response --evidence-backed
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-background rounded-sm border border-border">
                    <div className="text-foreground leading-relaxed text-sm whitespace-pre-wrap">
                      {result.answer}
                    </div>
                  </div>
                  {result.sql_query && (
                    <details className="group">
                      <summary className="text-xs text-muted-foreground cursor-pointer hover:text-primary transition-colors flex items-center gap-2 font-mono uppercase tracking-wider">
                        <span className="text-primary">›</span>{" "}
                        generated_sql_query
                      </summary>
                      <pre className="mt-2 p-4 bg-background border border-border text-primary/80 rounded-sm text-xs overflow-x-auto font-mono">
                        {result.sql_query}
                      </pre>
                    </details>
                  )}
                </CardContent>
              </Card>

              {/* Results Table */}
              {result.results && result.results.length > 0 && (
                <Card className="border border-border bg-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-foreground font-mono text-sm">
                      <span className="text-primary">$</span>
                      results --count={result.results.length}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4">
                      {result.results.map((person, idx) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.1 }}
                        >
                          <Card className="border border-border hover:border-primary/50 transition-all bg-card">
                            <CardContent className="pt-6">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-3 mb-2">
                                    <h3 className="text-base font-semibold text-foreground font-mono">
                                      {person.name || `person_${idx + 1}`}
                                    </h3>
                                    {person.department && (
                                      <Badge
                                        variant="secondary"
                                        className="bg-background text-muted-foreground border border-border font-mono text-xs"
                                      >
                                        {person.department}
                                      </Badge>
                                    )}
                                  </div>

                                  <div className="space-y-2">
                                    {person.skill_name && (
                                      <div className="flex items-center gap-2">
                                        <Award className="w-4 h-4 text-primary" />
                                        <span className="text-sm font-medium text-primary">
                                          {person.skill_name}
                                        </span>
                                        {person.is_implicit && (
                                          <Badge
                                            variant="outline"
                                            className="text-xs border-primary/50 text-primary"
                                          >
                                            Implicit
                                          </Badge>
                                        )}
                                      </div>
                                    )}

                                    {person.confidence !== undefined && (
                                      <div className="space-y-1">
                                        <div className="flex items-center justify-between text-sm">
                                          <span className="text-muted-foreground">
                                            Confidence
                                          </span>
                                          <span className="font-semibold text-foreground">
                                            {person.confidence}%
                                          </span>
                                        </div>
                                        <Progress
                                          value={person.confidence}
                                          className="h-2"
                                        />
                                      </div>
                                    )}

                                    {person.evidence && (
                                      <p className="text-xs text-muted-foreground mt-2 font-mono border-l-2 border-primary/30 pl-3">
                                        {person.evidence.substring(0, 150)}...
                                      </p>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </motion.div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card className="border border-destructive/50 bg-destructive/10">
              <CardHeader>
                <CardTitle className="text-destructive font-mono text-sm flex items-center gap-2">
                  <span>$</span>
                  error --code=500
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-destructive/90 font-mono text-sm">
                  {result.error || "An error occurred"}
                </p>
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}

      {/* Empty State */}
      {!result && !loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="max-w-3xl mx-auto py-12"
        >
          <div className="text-center mb-8">
            <motion.div
              className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-linear-to-br from-primary/20 to-purple-600/20 mb-6 border-2 border-primary/30 shadow-lg shadow-primary/15"
              animate={{
                boxShadow: [
                  "0 0 15px rgba(155, 135, 245, 0.15)",
                  "0 0 25px rgba(155, 135, 245, 0.25)",
                  "0 0 15px rgba(155, 135, 245, 0.15)",
                ],
              }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Search className="w-10 h-10 text-primary" />
            </motion.div>
            <h3 className="text-2xl font-bold mb-3 bg-linear-to-r from-primary via-purple-400 to-primary bg-clip-text text-transparent">
              Hybrid Query System Ready
            </h3>
            <p className="text-muted-foreground max-w-2xl mx-auto text-base">
              NL-to-SQL for structured queries • RAG for document search •
              Fusion for complex analysis
            </p>
          </div>
          <div className="grid grid-cols-3 gap-4 text-left">
            <motion.div
              whileHover={{ scale: 1.03, y: -4 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <Card className="border-2 border-primary/30 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/15 transition-all bg-card/95 h-full">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 mb-2">
                    <Users className="w-5 h-5 text-primary" />
                    <h4 className="font-bold text-foreground text-sm">
                      Skill Matching
                    </h4>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Find experts by technical and implicit skills
                  </p>
                </CardContent>
              </Card>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.03, y: -4 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <Card className="border-2 border-primary/30 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/15 transition-all bg-card/95 h-full">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 mb-2">
                    <TrendingUp className="w-5 h-5 text-primary" />
                    <h4 className="font-bold text-foreground text-sm">
                      Gap Analysis
                    </h4>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Compare requirements vs. capabilities
                  </p>
                </CardContent>
              </Card>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.03, y: -4 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <Card className="border-2 border-primary/30 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/15 transition-all bg-card/95 h-full">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 mb-2">
                    <Award className="w-5 h-5 text-primary" />
                    <h4 className="font-bold text-foreground text-sm">
                      Team Assembly
                    </h4>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Build optimal teams for projects
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
