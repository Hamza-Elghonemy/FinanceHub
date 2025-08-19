"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { TableIcon, TrendingUp, TrendingDown } from "lucide-react"

export function FinancialTable({ data }) {
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

  const getProfitTrend = (current, previous) => {
    if (!previous) return null
    const change = ((current - previous) / previous) * 100
    return {
      percentage: Math.abs(change).toFixed(1),
      isPositive: change > 0,
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <TableIcon className="h-5 w-5 text-primary" />
          <CardTitle>Financial Data Table</CardTitle>
        </div>
        <CardDescription>Detailed quarterly financial performance data with trend indicators</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Year</TableHead>
                <TableHead>Quarter</TableHead>
                <TableHead className="text-right">Sales Volume</TableHead>
                <TableHead className="text-right">Profit</TableHead>
                <TableHead className="text-right">Profit Margin</TableHead>
                <TableHead className="text-right">Trend</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                    No data available for the selected filters
                  </TableCell>
                </TableRow>
              ) : (
                data.map((item, index) => {
                  const profitMargin = ((item.profit / item.sales_volume) * 100).toFixed(2)
                  const previousItem = index > 0 ? data[index - 1] : null
                  const trend = getProfitTrend(item.profit, previousItem?.profit)

                  return (
                    <TableRow key={`${item.year}-${item.quarter}`}>
                      <TableCell className="font-medium">{item.year}</TableCell>
                      <TableCell>Q{item.quarter}</TableCell>
                      <TableCell className="text-right font-mono">{formatNumber(item.sales_volume)}</TableCell>
                      <TableCell className="text-right font-mono">{formatCurrency(item.profit)}</TableCell>
                      <TableCell className="text-right">
                        <Badge variant={Number.parseFloat(profitMargin) > 10 ? "default" : "secondary"}>
                          {profitMargin}%
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        {trend && (
                          <div className="flex items-center justify-end gap-1">
                            {trend.isPositive ? (
                              <TrendingUp className="h-4 w-4 text-green-600" />
                            ) : (
                              <TrendingDown className="h-4 w-4 text-red-600" />
                            )}
                            <span
                              className={`text-sm font-medium ${trend.isPositive ? "text-green-600" : "text-red-600"}`}
                            >
                              {trend.percentage}%
                            </span>
                          </div>
                        )}
                      </TableCell>
                    </TableRow>
                  )
                })
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
