import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/dio_client.dart';

class DashboardState {
  final double totalPortfolioValue;
  final double dayPnl;
  final double dayPnlPercent;
  final double totalPnl;
  final double totalPnlPercent;
  final bool isPaperMode;
  final int openOrdersCount;
  final List<PositionItem> watchedPositions;
  final bool isLoading;

  const DashboardState({
    this.totalPortfolioValue = 0.0,
    this.dayPnl = 0.0,
    this.dayPnlPercent = 0.0,
    this.totalPnl = 0.0,
    this.totalPnlPercent = 0.0,
    this.isPaperMode = true,
    this.openOrdersCount = 0,
    this.watchedPositions = const [],
    this.isLoading = true,
  });

  DashboardState copyWith({
    double? totalPortfolioValue,
    double? dayPnl,
    double? dayPnlPercent,
    double? totalPnl,
    double? totalPnlPercent,
    bool? isPaperMode,
    int? openOrdersCount,
    List<PositionItem>? watchedPositions,
    bool? isLoading,
  }) {
    return DashboardState(
      totalPortfolioValue: totalPortfolioValue ?? this.totalPortfolioValue,
      dayPnl: dayPnl ?? this.dayPnl,
      dayPnlPercent: dayPnlPercent ?? this.dayPnlPercent,
      totalPnl: totalPnl ?? this.totalPnl,
      totalPnlPercent: totalPnlPercent ?? this.totalPnlPercent,
      isPaperMode: isPaperMode ?? this.isPaperMode,
      openOrdersCount: openOrdersCount ?? this.openOrdersCount,
      watchedPositions: watchedPositions ?? this.watchedPositions,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class PositionItem {
  final String symbol;
  final int quantity;
  final double currentPrice;
  final double pnl;

  const PositionItem({
    required this.symbol,
    required this.quantity,
    required this.currentPrice,
    required this.pnl,
  });
  
  factory PositionItem.fromJson(Map<String, dynamic> json) {
    return PositionItem(
      symbol: json['symbol'] ?? '',
      quantity: json['quantity'] ?? 0,
      currentPrice: (json['currentPrice'] ?? json['current_price'] ?? 0.0).toDouble(),
      pnl: (json['pnl'] ?? 0.0).toDouble(),
    );
  }
}

class DashboardController extends AsyncNotifier<DashboardState> {
  @override
  FutureOr<DashboardState> build() async {
    return _fetchDashboardData();
  }

  Future<DashboardState> _fetchDashboardData() async {
    try {
      final response = await dioClient.dio.get('/api/v1/portfolio/dashboard');
      final data = response.data;
      
      final positionsJson = data['watchedPositions'] as List? ?? data['watched_positions'] as List? ?? [];
      final positions = positionsJson.map((e) => PositionItem.fromJson(e)).toList();

      return DashboardState(
        totalPortfolioValue: (data['totalPortfolioValue'] ?? data['total_value'] ?? 0.0).toDouble(),
        dayPnl: (data['dayPnl'] ?? data['day_pnl'] ?? 0.0).toDouble(),
        dayPnlPercent: (data['dayPnlPercent'] ?? data['day_pnl_percent'] ?? 0.0).toDouble(),
        totalPnl: (data['totalPnl'] ?? data['total_pnl'] ?? 0.0).toDouble(),
        totalPnlPercent: (data['totalPnlPercent'] ?? data['total_pnl_percent'] ?? 0.0).toDouble(),
        isPaperMode: data['isPaperMode'] ?? data['is_paper_mode'] ?? true,
        openOrdersCount: data['openOrdersCount'] ?? data['open_orders_count'] ?? 0,
        watchedPositions: positions,
        isLoading: false,
      );
    } catch (e) {
      // Return safe fallback
      return const DashboardState(isLoading: false);
    }
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchDashboardData());
  }
}

final dashboardControllerProvider = AsyncNotifierProvider<DashboardController, DashboardState>(
  DashboardController.new,
);
