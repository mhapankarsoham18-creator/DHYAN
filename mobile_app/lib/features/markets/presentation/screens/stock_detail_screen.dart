import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/theme/app_theme.dart';
import 'package:fl_chart/fl_chart.dart';

import 'package:mobile_app/core/services/ai_service.dart';
import 'package:mobile_app/features/analytics/presentation/widgets/ai_insight_line.dart';
import 'package:mobile_app/features/analytics/presentation/widgets/sentiment_badge.dart';
import 'package:mobile_app/features/analytics/presentation/widgets/pattern_reports.dart';
import 'package:mobile_app/features/analytics/presentation/widgets/legal_disclaimer.dart';

class StockDetailScreen extends ConsumerStatefulWidget {
  final String symbol;

  const StockDetailScreen({super.key, required this.symbol});

  @override
  ConsumerState<StockDetailScreen> createState() => _StockDetailScreenState();
}

class _StockDetailScreenState extends ConsumerState<StockDetailScreen> {
  String _selectedTimeframe = '1D';
  final List<String> _timeframes = ['1D', '1W', '1M', '1Y', 'ALL'];

  late Future<String> _insightFuture;
  late Future<SentimentResult> _sentimentFuture;

  @override
  void initState() {
    super.initState();
    _fetchAI();
  }

  void _fetchAI() {
    final aiService = ref.read(aiServiceProvider);
    
    // Triggering AI requests deterministically based on fake chart state for demo
    _insightFuture = aiService.getChartInsight(
      symbol: widget.symbol,
      rsi: 28.5, // Oversold
      macdSignal: 'bearish_cross',
      priceVs52wHigh: -12.4,
      priceVs52wLow: 3.2, // Near 52w low
      trend: 'downtrend',
    );

    _sentimentFuture = aiService.getSentiment(
      symbol: widget.symbol,
      headlines: [
        "${widget.symbol} announces new strategic partnership.",
        "Revenue margins remain tight for ${widget.symbol}.",
        "Global headwinds affect ${widget.symbol} stock prices."
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text(widget.symbol, style: const TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(icon: const Icon(Icons.star_border), onPressed: () {}),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(),
            const SizedBox(height: 16),
            
            // AI Sentiment Badge
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: FutureBuilder<SentimentResult>(
                future: _sentimentFuture,
                builder: (context, snapshot) {
                  if (!snapshot.hasData) return const SizedBox.shrink();
                  return SentimentBadge(result: snapshot.data!);
                },
              ),
            ),
            
            const SizedBox(height: 24),
            _buildChartArea(),
            const SizedBox(height: 8),

            // The Chart Timeframe Slider
            _buildTimeframeSlider(),
            const SizedBox(height: 8),

            // AI Insight Line (hooked below chart)
            AiInsightLine(insightFuture: _insightFuture),
            const SizedBox(height: 32),

            // Feature 2 Hook: Explainer Tap
            _buildPatternDetector(),

            const SizedBox(height: 40),
            // Placeholder for buy/sell
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Row(
                children: [
                   Expanded(
                     child: ElevatedButton(
                       style: ElevatedButton.styleFrom(backgroundColor: AppTheme.danger, padding: const EdgeInsets.symmetric(vertical: 16)),
                       onPressed: () {},
                       child: const Text("SELL", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                     ),
                   ),
                   const SizedBox(width: 16),
                   Expanded(
                     child: ElevatedButton(
                       style: ElevatedButton.styleFrom(backgroundColor: AppTheme.success, padding: const EdgeInsets.symmetric(vertical: 16)),
                       onPressed: () {},
                       child: const Text("BUY", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                     ),
                   ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Mandatory SEBI / App Store legal disclaimer
            const LegalDisclaimer(),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return const Padding(
      padding: EdgeInsets.symmetric(horizontal: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '₹2,540.00',
            style: TextStyle(color: AppTheme.textPrimary, fontSize: 32, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 4),
          Text(
            '-₹45.50 (1.76%) Today',
            style: TextStyle(color: AppTheme.danger, fontSize: 14, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildChartArea() {
    return Container(
      height: 250,
      padding: const EdgeInsets.only(right: 16),
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: false),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (val, meta) => Text(val.toStringAsFixed(0), style: const TextStyle(color: AppTheme.textSecondary, fontSize: 10)),
              )
            ),
            bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: const [
                FlSpot(0, 2600), FlSpot(1, 2580), FlSpot(2, 2585),
                FlSpot(3, 2550), FlSpot(4, 2570), FlSpot(5, 2540),
              ],
              isCurved: true,
              color: AppTheme.danger,
              barWidth: 2,
              isStrokeCapRound: true,
              dotData: FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: AppTheme.danger.withValues(alpha: 0.1),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeframeSlider() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: _timeframes.map((tf) {
          final isSelected = tf == _selectedTimeframe;
          return GestureDetector(
            onTap: () {
              setState(() {
                _selectedTimeframe = tf;
                _fetchAI(); // Refetch AI insight upon zooming chart timeframe
              });
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              decoration: BoxDecoration(
                color: isSelected ? AppTheme.surfaceVariant : Colors.transparent,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                tf,
                style: TextStyle(
                  color: isSelected ? AppTheme.textPrimary : AppTheme.textSecondary,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildPatternDetector() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: GestureDetector(
        onTap: () {
          showPatternExplainer(
            context,
            "Morning Star",
            widget.symbol,
            ref.read(aiServiceProvider)
          );
        },
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppTheme.surface,
            border: Border.all(color: AppTheme.surfaceVariant),
            borderRadius: BorderRadius.circular(8),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.2),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: const Row(
            children: [
              Icon(Icons.candlestick_chart, color: AppTheme.primary),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                     Text('Pattern Detected: Morning Star', style: TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.bold, fontSize: 13)),
                     SizedBox(height: 2),
                     Text('Tap for AI Explanation', style: TextStyle(color: AppTheme.textSecondary, fontSize: 11)),
                  ],
                ),
              ),
              Icon(Icons.chevron_right, color: AppTheme.textSecondary, size: 20),
            ],
          ),
        ),
      ),
    );
  }
}
