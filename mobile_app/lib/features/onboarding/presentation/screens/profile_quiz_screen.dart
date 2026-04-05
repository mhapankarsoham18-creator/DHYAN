import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile_app/core/theme/app_theme.dart';

class ProfileQuizScreen extends StatefulWidget {
  const ProfileQuizScreen({super.key});

  @override
  State<ProfileQuizScreen> createState() => _ProfileQuizScreenState();
}

class _ProfileQuizScreenState extends State<ProfileQuizScreen> {
  int _currentStep = 0;
  final List<Map<String, dynamic>> _questions = [
    {
      'question': 'What is your trading experience?',
      'options': ['Beginner', 'Intermediate', 'Pro'],
      'icon': Icons.trending_up,
    },
    {
      'question': 'What is your risk tolerance?',
      'options': ['Conservative', 'Moderate', 'Aggressive'],
      'icon': Icons.warning_amber,
    },
    {
      'question': 'Your primary financial goal?',
      'options': ['Wealth Building', 'Regular Income', 'Capital Preservation'],
      'icon': Icons.stars,
    },
    {
      'question': 'Do you have a commerce background?',
      'options': ['Yes, I understand finance', 'No, I\'m new to terms'],
      'icon': Icons.school,
    },
    {
      'question': 'Preferred trading style?',
      'options': ['Intraday', 'Swing', 'Long-term'],
      'icon': Icons.timer,
    },
  ];

  void _nextStep() {
    if (_currentStep < _questions.length - 1) {
      setState(() => _currentStep++);
    } else {
      context.goNamed('home');
    }
  }

  @override
  Widget build(BuildContext context) {
    final q = _questions[_currentStep];
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text('Step ${_currentStep + 1} of 5'),
        leading: IconButton(
          onPressed: _currentStep == 0 ? null : () => setState(() => _currentStep--),
          icon: const Icon(Icons.arrow_back),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          children: [
            LinearProgressIndicator(
              value: (_currentStep + 1) / 5,
              backgroundColor: AppTheme.surface,
              valueColor: const AlwaysStoppedAnimation(AppTheme.primary),
              minHeight: 8,
              borderRadius: BorderRadius.circular(4),
            ),
            const Spacer(),
            Icon(q['icon'], size: 80, color: AppTheme.primary),
            const SizedBox(height: 32),
            Text(
              q['question'],
              textAlign: TextAlign.center,
              style: const TextStyle(color: AppTheme.textPrimary, fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const Spacer(),
            ...List.generate(
              q['options'].length,
              (index) => Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: SizedBox(
                  width: double.infinity,
                  height: 60,
                  child: OutlinedButton(
                    onPressed: _nextStep,
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: AppTheme.surfaceVariant),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      backgroundColor: AppTheme.surface,
                    ),
                    child: Text(
                      q['options'][index],
                      style: const TextStyle(color: AppTheme.textPrimary, fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ),
            ),
            const Spacer(),
          ],
        ),
      ),
    );
  }
}
