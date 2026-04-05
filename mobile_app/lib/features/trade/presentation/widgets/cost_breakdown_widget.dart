import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/theme/app_theme.dart';
import '../controllers/trade_controller.dart';

class CostBreakdownWidget extends ConsumerWidget {
  const CostBreakdownWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(tradeControllerProvider).value;
    final controller = ref.watch(tradeControllerProvider.notifier);

    if (state == null) return const SizedBox.shrink();

    final cost = controller.estimatedCost;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.surfaceVariant),
      ),
      child: Column(
        children: [
          _CostRow(label: 'Est. Trade Value', value: '₹${(state.quantity * (state.orderType == 'Market' ? 2540.0 : state.price)).toStringAsFixed(2)}'),
          const SizedBox(height: 8),
          _CostRow(label: 'Brokerage (${state.productType})', value: state.productType == 'MIS' ? '₹20.00' : '₹0.00', isGreen: state.productType == 'CNC'),
          const SizedBox(height: 8),
          const _CostRow(label: 'Statutory Charges', value: '₹2.45'),
          const Divider(color: AppTheme.surfaceVariant, height: 24),
          _CostRow(
            label: 'Total Margin Required',
            value: '₹${cost.toStringAsFixed(2)}',
            isBold: true,
          ),
        ],
      ),
    );
  }
}

class _CostRow extends StatelessWidget {
  final String label;
  final String value;
  final bool isGreen;
  final bool isBold;

  const _CostRow({
    required this.label,
    required this.value,
    this.isGreen = false,
    this.isBold = false,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            color: AppTheme.textSecondary,
            fontSize: 14,
            fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            color: isGreen ? AppTheme.success : AppTheme.textPrimary,
            fontSize: 14,
            fontWeight: isBold ? FontWeight.bold : FontWeight.bold,
          ),
        ),
      ],
    );
  }
}
