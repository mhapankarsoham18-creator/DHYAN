import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/theme/app_theme.dart';
import 'package:mobile_app/core/providers/app_settings_provider.dart';
import '../controllers/trade_controller.dart';

class OrderFormWidget extends ConsumerStatefulWidget {
  const OrderFormWidget({super.key});

  @override
  ConsumerState<OrderFormWidget> createState() => _OrderFormWidgetState();
}

class _OrderFormWidgetState extends ConsumerState<OrderFormWidget> {
  final TextEditingController _qtyController = TextEditingController(text: '1');
  final TextEditingController _priceController = TextEditingController();

  @override
  void dispose() {
    _qtyController.dispose();
    _priceController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(tradeControllerProvider).value;
    final controller = ref.watch(tradeControllerProvider.notifier);
    final settingsNotifier = ref.read(appSettingsProvider.notifier);
    if (state == null) return const Center(child: CircularProgressIndicator());

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildProductAndOrderType(state, controller, settingsNotifier),
        const SizedBox(height: 24),
        _buildInputs(state, controller),
      ],
    );
  }

  Widget _buildProductAndOrderType(
    TradeFormState state,
    TradeController controller,
    AppSettingsNotifier notifier,
  ) {
    final productItems = {
      'CNC': notifier.translate('CNC', 'Delivery'),
      'MIS': notifier.translate('MIS', 'Intraday'),
      'NRML': notifier.translate('NRML', 'Normal'),
    };

    return Row(
      children: [
        Expanded(
          child: _buildDropdown(
            'Product',
            state.productType,
            productItems.keys.toList(),
            (v) => controller.updateProduct(v!),
            itemLabels: productItems,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildDropdown(
            'Order',
            state.orderType,
            ['Market', 'Limit', 'SL', 'SL-M'],
            (v) {
              controller.updateOrderType(v!);
              if (v == 'Market') {
                _priceController.clear();
                controller.updatePrice(0.0);
              }
            },
          ),
        ),
      ],
    );
  }

  Widget _buildDropdown(
    String label,
    String value,
    List<String> items,
    ValueChanged<String?> onChanged, {
    Map<String, String>? itemLabels,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          decoration: BoxDecoration(
            color: AppTheme.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppTheme.surfaceVariant),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: value,
              dropdownColor: AppTheme.surface,
              icon: const Icon(Icons.keyboard_arrow_down, color: AppTheme.textSecondary),
              isExpanded: true,
              items: items
                  .map(
                    (e) => DropdownMenuItem(
                      value: e,
                      child: Text(
                        itemLabels?[e] ?? e,
                        style: const TextStyle(color: AppTheme.textPrimary),
                      ),
                    ),
                  )
                  .toList(),
              onChanged: onChanged,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildInputs(TradeFormState state, TradeController controller) {
    return Row(
      children: [
        Expanded(
          child: _buildInputField(
            'Quantity',
            _qtyController,
            isNumeric: true,
            onChanged: (v) => controller.updateQuantity(int.tryParse(v) ?? 0),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildInputField(
            'Price (₹)',
            _priceController,
            isNumeric: true,
            enabled: state.orderType != 'Market',
            hint: 'Market',
            onChanged: (v) => controller.updatePrice(double.tryParse(v) ?? 0.0),
          ),
        ),
      ],
    );
  }

  Widget _buildInputField(
    String label,
    TextEditingController textCtrl, {
    bool isNumeric = false,
    bool enabled = true,
    String? hint,
    ValueChanged<String>? onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: textCtrl,
          enabled: enabled,
          keyboardType: isNumeric ? const TextInputType.numberWithOptions(decimal: true) : TextInputType.text,
          onChanged: onChanged,
          style: TextStyle(
            color: enabled ? AppTheme.textPrimary : AppTheme.textSecondary,
          ),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: const TextStyle(color: AppTheme.textSecondary),
            filled: true,
            fillColor: AppTheme.surface,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: AppTheme.surfaceVariant),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: AppTheme.primary),
            ),
            disabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: AppTheme.surfaceVariant, width: 0.5),
            ),
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          ),
        ),
      ],
    );
  }
}
