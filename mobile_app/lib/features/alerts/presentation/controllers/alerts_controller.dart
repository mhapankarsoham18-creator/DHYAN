import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/dio_client.dart';

class AlertItem {
  final String id;
  final String symbol;
  final String condition;
  final String timeText;
  final bool isTriggered;
  final String? resultText;

  AlertItem({
    required this.id,
    required this.symbol,
    required this.condition,
    required this.timeText,
    this.isTriggered = false,
    this.resultText,
  });

  factory AlertItem.fromJson(Map<String, dynamic> json) {
    return AlertItem(
      id: json['id'].toString(),
      symbol: json['symbol'] ?? '',
      condition: json['condition_text'] ?? '',
      timeText: json['created_at_text'] ?? 'Recently',
      isTriggered: json['is_triggered'] ?? false,
      resultText: json['result_text'],
    );
  }
}

class AlertsState {
  final List<AlertItem> activeAlerts;
  final List<AlertItem> alertHistory;
  final bool isLoading;

  const AlertsState({
    this.activeAlerts = const [],
    this.alertHistory = const [],
    this.isLoading = false,
  });

  AlertsState copyWith({
    List<AlertItem>? activeAlerts,
    List<AlertItem>? alertHistory,
    bool? isLoading,
  }) {
    return AlertsState(
      activeAlerts: activeAlerts ?? this.activeAlerts,
      alertHistory: alertHistory ?? this.alertHistory,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class AlertsController extends AsyncNotifier<AlertsState> {
  @override
  FutureOr<AlertsState> build() async {
    return _fetchAlerts();
  }

  Future<AlertsState> _fetchAlerts() async {
    try {
      final response = await dioClient.dio.get('/api/v1/alerts');
      final data = response.data['data'] as List?;
      if (data == null) return const AlertsState();
      
      final active = <AlertItem>[];
      final history = <AlertItem>[];
      
      for (final item in data) {
        final alert = AlertItem.fromJson(item);
        if (alert.isTriggered) {
          history.add(alert);
        } else {
          active.add(alert);
        }
      }
      return AlertsState(activeAlerts: active, alertHistory: history);
    } catch (e) {
      // Return empty state or fallback to previous state if error occurs
      return state.value ?? const AlertsState();
    }
  }

  Future<void> addAlert(String symbol, String condition, double targetValue) async {
    final currentState = state.value;
    if (currentState == null) return;
    state = AsyncData(currentState.copyWith(isLoading: true));
    
    try {
      await dioClient.dio.post('/api/v1/alerts', data: {
        'symbol': symbol,
        'condition': condition,
        'target_value': targetValue,
      });
      
      // Refresh list
      state = AsyncData(await _fetchAlerts());
    } catch (e) {
      state = AsyncData(currentState.copyWith(isLoading: false));
    }
  }

  Future<void> deleteAlert(String id) async {
    final currentState = state.value;
    if (currentState == null) return;

    try {
      final updatedActive = currentState.activeAlerts.where((a) => a.id != id).toList();
      state = AsyncData(currentState.copyWith(activeAlerts: updatedActive)); // Optimistic UI
      
      await dioClient.dio.delete('/api/v1/alerts/$id');
    } catch (e) {
      // Revert on failure by refetching
      state = AsyncData(await _fetchAlerts());
    }
  }
}

final alertsControllerProvider = AsyncNotifierProvider<AlertsController, AlertsState>(
  AlertsController.new,
);
