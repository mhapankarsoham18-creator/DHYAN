import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:mobile_app/core/theme/app_theme.dart';
import '../controllers/dashboard_controller.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stateAsync = ref.watch(dashboardControllerProvider);
    final notifier = ref.read(dashboardControllerProvider.notifier);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => Scaffold.of(context).openDrawer(),
          icon: const Icon(Icons.menu_rounded, size: 22),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _getGreeting(),
              style: AppTheme.bodySmall.copyWith(color: AppTheme.textTertiary, fontSize: 11),
            ),
            const Text('Overview', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 18, fontFamily: AppTheme.fontHeadline)),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.notifications_none_rounded, color: AppTheme.textSecondary, size: 22),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: notifier.refresh,
        color: AppTheme.primary,
        backgroundColor: AppTheme.surface,
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
          slivers: [
            SliverPadding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              sliver: SliverToBoxAdapter(
                child: stateAsync.when(
                  loading: () => _buildLoadingSkeleton(),
                  error: (e, st) => _buildErrorState(e.toString(), notifier.refresh),
                  data: (data) => _buildDashboardContent(context, data),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  }

  Widget _buildLoadingSkeleton() {
    return Column(
      children: List.generate(3, (i) => Padding(
        padding: EdgeInsets.only(bottom: 16),
        child: Container(
          height: i == 0 ? 180 : 80,
          decoration: AppTheme.premiumCard(),
        ),
      )),
    );
  }

  Widget _buildErrorState(String error, VoidCallback onRetry) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.danger.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.cloud_off_rounded, color: AppTheme.danger, size: 32),
            ),
            const SizedBox(height: 16),
            Text('Connection Issue', style: AppTheme.headlineSmall),
            const SizedBox(height: 8),
            Text(error, style: AppTheme.bodyMedium, textAlign: TextAlign.center),
            const SizedBox(height: 20),
            TextButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded, size: 18),
              label: const Text('Retry'),
              style: TextButton.styleFrom(foregroundColor: AppTheme.primary),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboardContent(BuildContext context, DashboardState data) {
    if (data.isLoading) return _buildLoadingSkeleton();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ── Portfolio Card ──────────────────────
        _buildPortfolioCard(data),
        const SizedBox(height: 24),

        // ── Performance Chart ──────────────────
        _buildPerformanceChart(data),
        const SizedBox(height: 24),

        // ── Quick Stats ────────────────────────
        Row(
          children: [
            Expanded(child: _buildStatCard(
              'Today\'s Return',
              '₹${data.dayPnl.toStringAsFixed(0)}',
              '${data.dayPnlPercent >= 0 ? '+' : ''}${data.dayPnlPercent.toStringAsFixed(2)}%',
              data.dayPnl >= 0 ? AppTheme.success : AppTheme.danger,
              Icons.trending_up_rounded,
            )),
            const SizedBox(width: 12),
            Expanded(child: _buildStatCard(
              'Open Orders',
              '${data.openOrdersCount}',
              'Pending',
              AppTheme.accent,
              Icons.pending_actions_rounded,
            )),
          ],
        ),
        const SizedBox(height: 28),

        // ── Watchlist ──────────────────────────
        if (data.watchedPositions.isNotEmpty) ...[
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Positions', style: AppTheme.headlineSmall),
              Text('${data.watchedPositions.length} active', style: AppTheme.bodySmall),
            ],
          ),
          const SizedBox(height: 12),
          ...data.watchedPositions.map((pos) => _buildPositionTile(pos)),
        ] else
          _buildEmptyPositions(),

        const SizedBox(height: 48),
      ],
    );
  }

  Widget _buildPortfolioCard(DashboardState data) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF1A2636), Color(0xFF141C28)],
        ),
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(color: AppTheme.surfaceVariant.withValues(alpha: 0.4), width: 0.5),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primary.withValues(alpha: 0.08),
            blurRadius: 40,
            offset: const Offset(0, 16),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Equity Value', style: AppTheme.bodyMedium.copyWith(fontSize: 13)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: data.isPaperMode
                      ? AppTheme.primary.withValues(alpha: 0.12)
                      : AppTheme.success.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  data.isPaperMode ? 'PAPER' : 'LIVE',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1,
                    color: data.isPaperMode ? AppTheme.primary : AppTheme.success,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            '₹${_formatNumber(data.totalPortfolioValue)}',
            style: AppTheme.numberLarge,
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(child: _buildMiniStat('Day P&L', '${data.dayPnl >= 0 ? '+' : ''}₹${data.dayPnl.toStringAsFixed(0)}', data.dayPnl >= 0)),
              Container(width: 0.5, height: 36, color: AppTheme.surfaceVariant.withValues(alpha: 0.5)),
              const SizedBox(width: 20),
              Expanded(child: _buildMiniStat('Total P&L', '${data.totalPnl >= 0 ? '+' : ''}₹${data.totalPnl.toStringAsFixed(0)}', data.totalPnl >= 0)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMiniStat(String label, String value, bool isPositive) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTheme.bodySmall.copyWith(fontSize: 11)),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontFamily: AppTheme.fontHeadline,
            color: isPositive ? AppTheme.success : AppTheme.danger,
            fontSize: 16,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }

  Widget _buildPerformanceChart(DashboardState data) {
    // Generate sample chart data (in production, this comes from backend history)
    final spots = List.generate(24, (i) {
      final base = data.totalPortfolioValue > 0 ? data.totalPortfolioValue : 100000;
      final variation = (i - 12) * (base * 0.002) + (i * i * 0.5);
      return FlSpot(i.toDouble(), base + variation);
    });

    final isPositive = spots.last.y >= spots.first.y;
    final chartColor = isPositive ? AppTheme.success : AppTheme.danger;

    return Container(
      padding: const EdgeInsets.fromLTRB(16, 20, 16, 12),
      decoration: AppTheme.premiumCard(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Performance', style: AppTheme.headlineSmall.copyWith(fontSize: 15)),
              _buildChartTimeSelector(),
            ],
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 160,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  horizontalInterval: spots.last.y * 0.01,
                  getDrawingHorizontalLine: (value) => FlLine(
                    color: AppTheme.surfaceVariant.withValues(alpha: 0.3),
                    strokeWidth: 0.5,
                  ),
                ),
                titlesData: const FlTitlesData(show: false),
                borderData: FlBorderData(show: false),
                lineTouchData: LineTouchData(
                  touchTooltipData: LineTouchTooltipData(
                    getTooltipColor: (_) => AppTheme.surfaceElevated,
                    getTooltipItems: (spots) => spots.map((s) => LineTooltipItem(
                      '₹${s.y.toStringAsFixed(0)}',
                      TextStyle(
                        color: chartColor,
                        fontWeight: FontWeight.w600,
                        fontFamily: AppTheme.fontHeadline,
                        fontSize: 12,
                      ),
                    )).toList(),
                  ),
                ),
                lineBarsData: [
                  LineChartBarData(
                    spots: spots,
                    isCurved: true,
                    curveSmoothness: 0.35,
                    color: chartColor,
                    barWidth: 2,
                    isStrokeCapRound: true,
                    dotData: const FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          chartColor.withValues(alpha: 0.2),
                          chartColor.withValues(alpha: 0.0),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              duration: const Duration(milliseconds: 600),
              curve: Curves.easeOutCubic,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChartTimeSelector() {
    final periods = ['1D', '1W', '1M', '3M', '1Y'];
    return Row(
      children: periods.map((p) {
        final isSelected = p == '1W';
        return Padding(
          padding: const EdgeInsets.only(left: 4),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: isSelected ? AppTheme.primary.withValues(alpha: 0.15) : Colors.transparent,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              p,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                color: isSelected ? AppTheme.primary : AppTheme.textTertiary,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildStatCard(String label, String value, String sub, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: AppTheme.premiumCard(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 18),
          ),
          const SizedBox(height: 14),
          Text(label, style: AppTheme.bodySmall.copyWith(fontSize: 12)),
          const SizedBox(height: 4),
          Text(value, style: AppTheme.numberMedium.copyWith(fontSize: 20)),
          const SizedBox(height: 2),
          Text(sub, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _buildPositionTile(PositionItem pos) {
    final isPos = pos.pnl >= 0;
    final color = isPos ? AppTheme.success : AppTheme.danger;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: AppTheme.premiumCard(),
      child: Row(
        children: [
          // Symbol badge
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppTheme.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Center(
              child: Text(
                pos.symbol.substring(0, pos.symbol.length > 2 ? 2 : pos.symbol.length),
                style: TextStyle(
                  color: AppTheme.primary,
                  fontWeight: FontWeight.w700,
                  fontSize: 13,
                  fontFamily: AppTheme.fontHeadline,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(pos.symbol, style: const TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.w600, fontSize: 14)),
                const SizedBox(height: 2),
                Text('${pos.quantity} Qty', style: AppTheme.bodySmall),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('₹${pos.currentPrice.toStringAsFixed(2)}', style: TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.w600, fontSize: 14, fontFamily: AppTheme.fontHeadline)),
              const SizedBox(height: 2),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  '${isPos ? '+' : ''}₹${pos.pnl.toStringAsFixed(0)}',
                  style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyPositions() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 48),
      alignment: Alignment.center,
      child: Column(
        children: [
          Icon(Icons.inbox_rounded, color: AppTheme.textTertiary.withValues(alpha: 0.4), size: 40),
          const SizedBox(height: 12),
          Text('No active positions', style: AppTheme.bodyMedium),
          const SizedBox(height: 4),
          Text('Start trading to see your portfolio here', style: AppTheme.bodySmall),
        ],
      ),
    );
  }

  String _formatNumber(double value) {
    if (value >= 10000000) return '${(value / 10000000).toStringAsFixed(2)} Cr';
    if (value >= 100000) return '${(value / 100000).toStringAsFixed(2)} L';
    return value.toStringAsFixed(2);
  }
}
