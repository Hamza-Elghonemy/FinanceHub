"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, LineChart, Line } from "recharts"
import { TrendingUp, BarChart3 } from "lucide-react"

const chartConfig = {
  sales_volume: {
    label: "Sales Volume",
    color: "hsl(var(--chart-1))",
  },
  profit: {
    label: "Profit",
    color: "hsl(var(--chart-2))",
  },
}

export function FinancialChart({ data = [] }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    }).format(value || 0)
  }

  const formatNumber = (value) => {
    return new Intl.NumberFormat("en-US").format(value || 0)
  }

  const chartData = (data || []).map((item) => ({
    ...item,
    period: `${item?.year || "N/A"} Q${item?.quarter || "N/A"}`,
    sales_volume: item?.sales_volume || 0,
    profit: item?.profit || 0,
  }))

  if (!data || data.length === 0) {
    return (
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary" />
              <CardTitle>Sales Volume Trends</CardTitle>
            </div>
            <CardDescription>No data available</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center h-[300px] text-muted-foreground">No data to display</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              <CardTitle>Profit Analysis</CardTitle>
            </div>
            <CardDescription>No data available</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center h-[300px] text-muted-foreground">No data to display</div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Sales Volume Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            <CardTitle>Sales Volume Trends</CardTitle>
          </div>
          <CardDescription>Quarterly sales volume performance over time</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" tick={{ fontSize: 12 }} tickLine={false} axisLine={false} />
                <YAxis tickFormatter={formatNumber} tick={{ fontSize: 12 }} tickLine={false} axisLine={false} />
                <ChartTooltip
                  content={<ChartTooltipContent />}
                  formatter={(value) => [formatNumber(value), "Sales Volume"]}
                />
                <Bar dataKey="sales_volume" fill="var(--color-chart-1)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* Profit Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            <CardTitle>Profit Analysis</CardTitle>
          </div>
          <CardDescription>Quarterly profit trends and growth patterns</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" tick={{ fontSize: 12 }} tickLine={false} axisLine={false} />
                <YAxis tickFormatter={formatCurrency} tick={{ fontSize: 12 }} tickLine={false} axisLine={false} />
                <ChartTooltip
                  content={<ChartTooltipContent />}
                  formatter={(value) => [formatCurrency(value), "Profit"]}
                />
                <Line
                  type="monotone"
                  dataKey="profit"
                  stroke="var(--color-chart-2)"
                  strokeWidth={3}
                  dot={{ fill: "var(--color-chart-2)", strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: "var(--color-chart-2)", strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>
    </div>
  )
}
