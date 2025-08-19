"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, DollarSign, BarChart3, Target, Percent } from "lucide-react"

export function MetricsCards({ data }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    }).format(value)
  }

  const formatNumber = (value) => {
    return new Intl.NumberFormat("en-US").format(value)
  }

  const calculateMetrics = () => {
    if (!data || data.length === 0) {
      return {
        totalSales: 0,
        totalProfit: 0,
        avgProfitMargin: 0,
        growthRate: 0,
        isGrowthPositive: false,
      }
    }

    const totalSales = data.reduce((sum, item) => sum + item.sales_volume, 0)
    const totalProfit = data.reduce((sum, item) => sum + item.profit, 0)
    const avgProfitMargin = (totalProfit / totalSales) * 100

    // Calculate growth rate (comparing first and last quarters)
    const firstQuarter = data[0]
    const lastQuarter = data[data.length - 1]
    const growthRate =
      firstQuarter && lastQuarter ? ((lastQuarter.profit - firstQuarter.profit) / firstQuarter.profit) * 100 : 0

    return {
      totalSales,
      totalProfit,
      avgProfitMargin,
      growthRate: Math.abs(growthRate),
      isGrowthPositive: growthRate > 0,
    }
  }

  const metrics = calculateMetrics()

  const cards = [
    {
      title: "Total Sales Volume",
      value: formatNumber(metrics.totalSales),
      description: "Cumulative sales across all periods",
      icon: BarChart3,
      trend: null,
    },
    {
      title: "Total Profit",
      value: formatCurrency(metrics.totalProfit),
      description: "Total profit generated",
      icon: DollarSign,
      trend: null,
    },
    {
      title: "Average Profit Margin",
      value: `${metrics.avgProfitMargin.toFixed(2)}%`,
      description: "Overall profitability ratio",
      icon: Percent,
      trend: {
        value: metrics.avgProfitMargin,
        isPositive: metrics.avgProfitMargin > 10,
        label: metrics.avgProfitMargin > 10 ? "Healthy" : "Below Target",
      },
    },
    {
      title: "Growth Rate",
      value: `${metrics.growthRate.toFixed(1)}%`,
      description: "Period-over-period growth",
      icon: Target,
      trend: {
        value: metrics.growthRate,
        isPositive: metrics.isGrowthPositive,
        label: metrics.isGrowthPositive ? "Growing" : "Declining",
      },
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, index) => {
        const Icon = card.icon
        return (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{card.value}</div>
              <div className="flex items-center justify-between mt-2">
                <p className="text-xs text-muted-foreground">{card.description}</p>
                {card.trend && (
                  <div className="flex items-center gap-1">
                    {card.trend.isPositive ? (
                      <TrendingUp className="h-3 w-3 text-green-600" />
                    ) : (
                      <TrendingDown className="h-3 w-3 text-red-600" />
                    )}
                    <Badge variant={card.trend.isPositive ? "default" : "secondary"} className="text-xs">
                      {card.trend.label}
                    </Badge>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
