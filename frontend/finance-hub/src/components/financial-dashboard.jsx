"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { FinancialChart } from "@/components/financial-chart"
import { FinancialTable } from "@/components/financial-table"
import { ExportButtons } from "@/components/export-buttons"
import { MetricsCards } from "@/components/metrics-cards"
import { ThemeToggle } from "@/components/theme-toggle"
import { BarChart3, TrendingUp, Filter } from "lucide-react"

// Sample data matching the JSON structure
const sampleData = {
  food: {
    MC: {
      2023: [
        { quarter: 1, sales_volume: 1000, profit: 100 },
        { quarter: 2, sales_volume: 2000, profit: 50 },
        { quarter: 3, sales_volume: 1800, profit: 120 },
        { quarter: 4, sales_volume: 2200, profit: 180 },
      ],
      2024: [
        { quarter: 1, sales_volume: 2100, profit: 150 },
        { quarter: 2, sales_volume: 2400, profit: 200 },
        { quarter: 3, sales_volume: 2600, profit: 220 },
        { quarter: 4, sales_volume: 2800, profit: 250 },
      ],
    },
  },
  technology: {
    TECH: {
      2023: [
        { quarter: 1, sales_volume: 5000, profit: 800 },
        { quarter: 2, sales_volume: 5500, profit: 900 },
        { quarter: 3, sales_volume: 6000, profit: 1000 },
        { quarter: 4, sales_volume: 6200, profit: 1100 },
      ],
      2024: [
        { quarter: 1, sales_volume: 6500, profit: 1200 },
        { quarter: 2, sales_volume: 7000, profit: 1300 },
        { quarter: 3, sales_volume: 7200, profit: 1400 },
        { quarter: 4, sales_volume: 7500, profit: 1500 },
      ],
    },
  },
}

export function FinancialDashboard() {
  const [selectedCategory, setSelectedCategory] = useState("food")
  const [selectedYear, setSelectedYear] = useState("all")
  const [selectedCompany, setSelectedCompany] = useState("MC")

  const categories = Object.keys(sampleData)
  const companies = Object.keys(sampleData[selectedCategory] || {})
  const years = ["all", "2023", "2024"]

  const filteredData = useMemo(() => {
    const categoryData = sampleData[selectedCategory]
    if (!categoryData) return []

    const companyData = categoryData[selectedCompany]
    if (!companyData) return []

    if (selectedYear === "all") {
      return Object.entries(companyData).flatMap(([year, quarters]) =>
        quarters.map((q) => ({ ...q, year: Number.parseInt(year) })),
      )
    } else {
      const yearData = companyData[selectedYear]
      return yearData ? yearData.map((q) => ({ ...q, year: Number.parseInt(selectedYear) })) : []
    }
  }, [selectedCategory, selectedYear, selectedCompany])

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold">FinanceHub</h1>
            </div>
            <Badge variant="secondary" className="hidden sm:inline-flex">
              Professional
            </Badge>
          </div>

          <div className="flex items-center gap-4">
            <ExportButtons data={filteredData} />
            <ThemeToggle />
          </div>
        </div>
      </header>

      <div className="container mx-auto p-6 space-y-6">
        {/* Filters Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Filter className="h-5 w-5 text-primary" />
              <CardTitle>Filters & Controls</CardTitle>
            </div>
            <CardDescription>
              Customize your financial data view by selecting category, company, and time period
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Category</label>
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category} value={category}>
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Company</label>
                <Select value={selectedCompany} onValueChange={setSelectedCompany}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {companies.map((company) => (
                      <SelectItem key={company} value={company}>
                        {company}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Year</label>
                <Select value={selectedYear} onValueChange={setSelectedYear}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {years.map((year) => (
                      <SelectItem key={year} value={year}>
                        {year === "all" ? "All Years" : year}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Metrics Overview */}
        <MetricsCards data={filteredData} />

        {/* Main Content Tabs */}
        <Tabs defaultValue="charts" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="charts" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Charts & Analytics
            </TabsTrigger>
            <TabsTrigger value="table" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Data Table
            </TabsTrigger>
          </TabsList>

          <TabsContent value="charts" className="space-y-6">
            <FinancialChart data={filteredData} />
          </TabsContent>

          <TabsContent value="table" className="space-y-6">
            <FinancialTable data={filteredData} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
