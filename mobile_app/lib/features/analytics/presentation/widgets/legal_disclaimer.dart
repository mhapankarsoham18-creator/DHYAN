import 'package:flutter/material.dart';

/// Mandatory SEBI/App Store compliance disclaimer.
/// Must appear on every screen that shows any analysis, AI output, or chart data.
class LegalDisclaimer extends StatelessWidget {
  const LegalDisclaimer({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF30363D).withValues(alpha: 0.5)),
      ),
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.info_outline, color: Color(0xFF8B949E), size: 14),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              'This is for informational purposes only. Not investment advice. '
              'Consult a financial advisor before investing.',
              style: TextStyle(
                color: Color(0xFF8B949E),
                fontSize: 11,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
