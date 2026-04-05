import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/network/dio_client.dart';

// Provider for the AiService
final aiServiceProvider = Provider<AiService>((ref) {
  return AiService(dioClient.dio);
});

class AiService {
  final Dio _dio;
  AiService(this._dio);

  // ── Feature 1: Chart Insight ──────────────────────────
  Future<String> getChartInsight({
    required String symbol,
    double? rsi,
    String? macdSignal,
    required double priceVs52wHigh,
    required double priceVs52wLow,
    required String trend,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/ai/chart-insight',
        data: {
          'symbol': symbol,
          'rsi': rsi,
          'macd_signal': macdSignal,
          'price_vs_52w_high': priceVs52wHigh,
          'price_vs_52w_low': priceVs52wLow,
          'trend': trend,
        },
      ).timeout(const Duration(seconds: 6));
      return response.data['insight'] as String;
    } catch (_) {
      return ''; // Silently fail so the chart still renders without AI
    }
  }

  // ── Feature 2: Pattern Explainer ─────────────────────
  Future<String> explainPattern({
    required String patternName,
    required String symbol,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/ai/pattern-explain',
        data: {'pattern_name': patternName, 'symbol': symbol},
      ).timeout(const Duration(seconds: 6));
      return response.data['explanation'] as String;
    } catch (_) {
      return 'Pattern explanation unavailable.';
    }
  }

  // ── Feature 3: Sentiment Summary ─────────────────────
  Future<SentimentResult> getSentiment({
    required String symbol,
    required List<String> headlines,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/ai/sentiment',
        data: {
          'symbol': symbol,
          'headlines': headlines,
        },
      ).timeout(const Duration(seconds: 7));
      return SentimentResult.fromJson(response.data);
    } catch (_) {
      return SentimentResult.empty();
    }
  }

  // ── Feature 4 & 5: Weekly Reports ─────────────────────
  Future<String> getMarketWeeklyReport(double niftyPct, String sector) async {
    try {
      final res = await _dio.post('/api/v1/ai/reports/market-weekly', data: {
        'nifty_change_pct': niftyPct,
        'top_sector': sector,
      }).timeout(const Duration(seconds: 8));
      return res.data['report'] as String;
    } catch (_) {
      return 'Market report unavailable.';
    }
  }

  Future<String> getPortfolioWeeklyReport(int tradesCount, double winRate, double pnlPct) async {
    try {
      final res = await _dio.post('/api/v1/ai/reports/portfolio-weekly', data: {
        'trades_count': tradesCount,
        'win_rate': winRate,
        'pnl_percentage': pnlPct,
      }).timeout(const Duration(seconds: 8));
      return res.data['report'] as String;
    } catch (_) {
      return 'Portfolio report unavailable.';
    }
  }
}

class SentimentResult {
  final String summary;
  final String sentiment; // positive | negative | neutral

  const SentimentResult({
    required this.summary,
    required this.sentiment,
  });

  factory SentimentResult.fromJson(Map<String, dynamic> j) =>
      SentimentResult(
        summary: j['summary'] ?? '',
        sentiment: j['sentiment'] ?? 'neutral',
      );

  factory SentimentResult.empty() => const SentimentResult(
        summary: '',
        sentiment: 'neutral',
      );
}
