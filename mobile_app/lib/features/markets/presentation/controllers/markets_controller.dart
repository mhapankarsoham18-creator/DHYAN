import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/dio_client.dart';

class MarketIndex {
  final String symbol;
  final double latestPrice;
  final double change;
  final double changePercent;

  const MarketIndex({
    required this.symbol,
    required this.latestPrice,
    required this.change,
    required this.changePercent,
  });

  factory MarketIndex.fromJson(Map<String, dynamic> json) {
    return MarketIndex(
      symbol: json['symbol'] ?? '',
      latestPrice: (json['value'] ?? json['latestPrice'] ?? json['latest_price'] ?? 0.0).toDouble(),
      change: (json['change'] ?? 0.0).toDouble(),
      changePercent: (json['changePercent'] ?? json['change_percent'] ?? 0.0).toDouble(),
    );
  }
}

class MarketsState {
  final bool isMarketOpen;
  final List<MarketIndex> indices;
  final List<MarketIndex> topGainers;
  final List<MarketIndex> topLosers;
  final bool isLoading;
  final String? errorText;

  const MarketsState({
    this.isMarketOpen = false,
    this.indices = const [],
    this.topGainers = const [],
    this.topLosers = const [],
    this.isLoading = true,
    this.errorText,
  });

  MarketsState copyWith({
    bool? isMarketOpen,
    List<MarketIndex>? indices,
    List<MarketIndex>? topGainers,
    List<MarketIndex>? topLosers,
    bool? isLoading,
    String? errorText,
  }) {
    return MarketsState(
      isMarketOpen: isMarketOpen ?? this.isMarketOpen,
      indices: indices ?? this.indices,
      topGainers: topGainers ?? this.topGainers,
      topLosers: topLosers ?? this.topLosers,
      isLoading: isLoading ?? this.isLoading,
      errorText: errorText,
    );
  }
}

class MarketsController extends AsyncNotifier<MarketsState> {
  // We use a periodic timer for live polling
  Timer? _pollingTimer;

  @override
  FutureOr<MarketsState> build() async {
    ref.onDispose(() {
      _pollingTimer?.cancel();
    });
    
    // Start polling every 5 seconds for live market updates
    _pollingTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      if (!state.isLoading) _silentlyFetch();
    });

    return _fetchMarketsData();
  }

  Future<void> _silentlyFetch() async {
    try {
      final data = await _fetchMarketsData();
      state = AsyncData(data);
    } catch (_) {
      // Ignore background fetch errors
    }
  }

  Future<MarketsState> _fetchMarketsData() async {
    try {
      final response = await dioClient.dio.get('/api/v1/markets/overview');
      final data = response.data;
      
      final indicesJson = data['indices'] as List? ?? [];
      final gainersJson = data['topGainers'] as List? ?? data['top_gainers'] as List? ?? [];
      final losersJson = data['topLosers'] as List? ?? data['top_losers'] as List? ?? [];

      return MarketsState(
        isMarketOpen: data['is_market_open'] ?? false,
        indices: indicesJson.map((e) => MarketIndex.fromJson(e)).toList(),
        topGainers: gainersJson.map((e) => MarketIndex.fromJson(e)).toList(),
        topLosers: losersJson.map((e) => MarketIndex.fromJson(e)).toList(),
        isLoading: false,
      );
    } catch (e) {
      if (state.value != null) {
         return state.value!.copyWith(errorText: 'Live connection lost', isLoading: false);
      }
      return const MarketsState(isLoading: false, errorText: 'Failed to load market data.');
    }
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchMarketsData());
  }
}

final marketsControllerProvider = AsyncNotifierProvider<MarketsController, MarketsState>(
  MarketsController.new,
);
