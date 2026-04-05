import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../../../../core/network/dio_client.dart';

class TradeFormState {
  final String orderSide; // 'Buy' | 'Sell'
  final String productType; // 'CNC' | 'MIS' | 'NRML'
  final String orderType; // 'Market' | 'Limit' | 'SL' | 'SL-M'
  final int quantity;
  final double price;
  final bool isConfirming;
  final String? errorText;

  const TradeFormState({
    this.orderSide = 'Buy',
    this.productType = 'CNC',
    this.orderType = 'Market',
    this.quantity = 1,
    this.price = 0.0,
    this.isConfirming = false,
    this.errorText,
  });

  TradeFormState copyWith({
    String? orderSide,
    String? productType,
    String? orderType,
    int? quantity,
    double? price,
    bool? isConfirming,
    String? errorText,
  }) {
    return TradeFormState(
      orderSide: orderSide ?? this.orderSide,
      productType: productType ?? this.productType,
      orderType: orderType ?? this.orderType,
      quantity: quantity ?? this.quantity,
      price: price ?? this.price,
      isConfirming: isConfirming ?? this.isConfirming,
      errorText: errorText, // Optional null-clearing by omitting ??
    );
  }
}

class TradeController extends AsyncNotifier<TradeFormState> {
  @override
  FutureOr<TradeFormState> build() {
    return const TradeFormState();
  }

  void updateSide(String side) => state = AsyncData(state.value!.copyWith(orderSide: side));
  
  void updateProduct(String product) => state = AsyncData(state.value!.copyWith(productType: product));
  
  void updateOrderType(String type) => state = AsyncData(state.value!.copyWith(orderType: type));
  
  void updateQuantity(int qty) => state = AsyncData(state.value!.copyWith(quantity: qty));
  
  void updatePrice(double p) => state = AsyncData(state.value!.copyWith(price: p));

  Future<void> confirmOrder(String symbol) async {
    final currentState = state.value!;
    if (currentState.quantity <= 0) {
      state = AsyncData(currentState.copyWith(errorText: 'Quantity must be > 0'));
      return;
    }
    
    state = AsyncData(currentState.copyWith(isConfirming: true, errorText: null));
    
    try {
      final response = await dioClient.dio.post('/api/v1/orders/place', data: {
        'symbol': symbol,
        'side': currentState.orderSide.toUpperCase(),
        'product': currentState.productType,
        'order_type': currentState.orderType.toUpperCase(),
        'quantity': currentState.quantity,
        'price': currentState.orderType == 'Market' ? null : currentState.price,
      });

      if (response.statusCode == 200 || response.statusCode == 201) {
        state = AsyncData(currentState.copyWith(isConfirming: false, errorText: null));
        // We will dispatch a navigation event from the UI via a listener on successful state update, 
        // or trigger a confirmation dialog. For now, we rest safely in a non-loading state.
      } else {
        throw DioException(requestOptions: response.requestOptions, response: response);
      }
    } on DioException catch (e) {
      final msg = e.response?.data?['detail'] ?? e.message ?? 'Unknown network error';
      state = AsyncData(currentState.copyWith(isConfirming: false, errorText: 'Order failed: $msg'));
    } catch (e) {
      state = AsyncData(currentState.copyWith(isConfirming: false, errorText: 'Unexpected error: $e'));
    }
  }

  double get estimatedCost {
    final s = state.value!;
    final executionPrice = s.orderType == 'Market' ? 2540.0 : s.price;
    final total = executionPrice * s.quantity;
    final brokerage = s.productType == 'MIS' ? 20.0 : 0.0;
    final stt = 2.45;
    return total + brokerage + stt;
  }
}

final tradeControllerProvider = AsyncNotifierProvider<TradeController, TradeFormState>(
  TradeController.new,
);
