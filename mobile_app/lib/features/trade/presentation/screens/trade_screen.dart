import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/theme/app_theme.dart';

import '../controllers/trade_controller.dart';
import '../widgets/order_form_widget.dart';
import '../widgets/cost_breakdown_widget.dart';

class TradeScreen extends ConsumerWidget {
  final String symbol;
  final double currentPrice;

  const TradeScreen({super.key, this.symbol = 'RELIANCE', this.currentPrice = 0.0});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch state to react to changes, or manage loaders
    final stateAsync = ref.watch(tradeControllerProvider);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(title: const Text('Trade', style: TextStyle(fontWeight: FontWeight.bold))),
      // Always good to dismiss keyboard on tap outside in trade forms
      body: GestureDetector(
        onTap: () => FocusScope.of(context).unfocus(),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildStockHeaderCard(),
              const SizedBox(height: 24),
              _buildTypeSelector(ref),
              const SizedBox(height: 24),
              const OrderFormWidget(),
              const SizedBox(height: 32),
              const CostBreakdownWidget(),
              if (stateAsync.value?.errorText != null)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Text(
                    stateAsync.value!.errorText!,
                    style: TextStyle(color: AppTheme.danger, fontWeight: FontWeight.bold),
                  ),
                ),
              const SizedBox(height: 24),
              _buildActionButton(ref, stateAsync.value),
              const SizedBox(height: 24),
              _buildQuickTemplates(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStockHeaderCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.surfaceVariant),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.primary.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.show_chart, color: AppTheme.primary),
          ),
          const SizedBox(width: 16),
          const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Select Stock',
                style: TextStyle(
                  color: AppTheme.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                'Tap to search',
                style: TextStyle(color: AppTheme.textSecondary, fontSize: 14),
              ),
            ],
          ),
          const Spacer(),
          const Icon(Icons.keyboard_arrow_down, color: AppTheme.textSecondary),
        ],
      ),
    );
  }

  Widget _buildTypeSelector(WidgetRef ref) {
    final side = ref.watch(tradeControllerProvider).value?.orderSide ?? 'Buy';
    final controller = ref.watch(tradeControllerProvider.notifier);

    return Row(
      children: [
        Expanded(child: _buildTypeButton('Buy', AppTheme.success, side == 'Buy', () => controller.updateSide('Buy'))),
        const SizedBox(width: 16),
        Expanded(child: _buildTypeButton('Sell', AppTheme.danger, side == 'Sell', () => controller.updateSide('Sell'))),
      ],
    );
  }

  Widget _buildTypeButton(String type, Color color, bool isSelected, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? color : AppTheme.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? color : AppTheme.surfaceVariant,
          ),
          boxShadow: isSelected
              ? [BoxShadow(color: color.withValues(alpha: 0.3), blurRadius: 8, offset: const Offset(0, 3))]
              : [],
        ),
        alignment: Alignment.center,
        child: Text(
          type,
          style: TextStyle(
            color: isSelected ? Colors.white : AppTheme.textSecondary,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
      ),
    );
  }

  Widget _buildActionButton(WidgetRef ref, TradeFormState? state) {
    if (state == null) return const SizedBox.shrink();

    final isBuy = state.orderSide == 'Buy';
    final color = isBuy ? AppTheme.success : AppTheme.danger;
    
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: state.isConfirming
            ? null
            : () => ref.read(tradeControllerProvider.notifier).confirmOrder('RELIANCE'),
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          disabledBackgroundColor: color.withValues(alpha: 0.5),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          elevation: 0,
        ),
        child: state.isConfirming
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
              )
            : Text(
                'Confirm ${state.orderSide}',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
      ),
    );
  }

  Widget _buildQuickTemplates() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Quick Templates',
          style: TextStyle(
            color: AppTheme.textPrimary,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          physics: const BouncingScrollPhysics(),
          child: Row(
            children: [
              _buildTemplateChip('Scalp Buy 50'),
              _buildTemplateChip('SIP Reliance'),
              _buildTemplateChip('Exit All MIS'),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTemplateChip(String label) {
    return Container(
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.surfaceVariant),
      ),
      child: Text(
        label,
        style: const TextStyle(color: AppTheme.textPrimary, fontSize: 13, fontWeight: FontWeight.w500),
      ),
    );
  }
}
