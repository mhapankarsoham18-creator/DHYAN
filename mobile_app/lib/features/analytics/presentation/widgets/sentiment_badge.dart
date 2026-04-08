import 'package:flutter/material.dart';
import 'package:mobile_app/core/services/ai_service.dart';
import 'legal_disclaimer.dart';

class SentimentBadge extends StatelessWidget {
  final SentimentResult result;

  const SentimentBadge({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    if (result.summary.isEmpty) return const SizedBox.shrink();

    Color color;
    String icon;

    switch (result.sentiment) {
      case 'positive':
        color = const Color(0xFF2ECC71); // Green
        icon = '📈';
        break;
      case 'negative':
        color = const Color(0xFFE74C3C); // Red
        icon = '📉';
        break;
      case 'mixed':
        color = const Color(0xFFC9A84C); // Gold
        icon = '↔️';
        break;
      default:
        color = const Color(0xFF8B949E); // Grey
        icon = '➖';
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(6),
            border: Border.all(color: color.withValues(alpha: 0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(icon, style: const TextStyle(fontSize: 14)),
                  const SizedBox(width: 8),
                  Text(
                    'News Sentiment',
                    style: TextStyle(
                      color: color,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                result.summary,
                style: TextStyle(color: color.withValues(alpha: 0.9), fontSize: 13),
              ),
            ],
          ),
        ),
        const LegalDisclaimer(),
      ],
    );
  }
}
