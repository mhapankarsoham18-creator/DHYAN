import 'package:flutter_riverpod/flutter_riverpod.dart';

class AppSettings {
  final bool isSimpleMode;
  final bool isFocusMode;
  final bool isPremium;
  final String language;

  AppSettings({
    this.isSimpleMode = true,
    this.isFocusMode = false,
    this.isPremium = false,
    this.language = 'English',
  });

  AppSettings copyWith({
    bool? isSimpleMode,
    bool? isFocusMode,
    bool? isPremium,
    String? language,
  }) {
    return AppSettings(
      isSimpleMode: isSimpleMode ?? this.isSimpleMode,
      isFocusMode: isFocusMode ?? this.isFocusMode,
      isPremium: isPremium ?? this.isPremium,
      language: language ?? this.language,
    );
  }
}

class AppSettingsNotifier extends Notifier<AppSettings> {
  @override
  AppSettings build() {
    return AppSettings();
  }

  void toggleSimpleMode() {
    state = state.copyWith(isSimpleMode: !state.isSimpleMode);
  }

  void toggleFocusMode() {
    state = state.copyWith(isFocusMode: !state.isFocusMode);
  }

  void setPremium(bool value) {
    state = state.copyWith(isPremium: value);
  }

  void setLanguage(String lang) {
    state = state.copyWith(language: lang);
  }
  
  // Method to translate jargon if simple mode is on
  String translate(String term, String simplified) {
    return state.isSimpleMode ? simplified : term;
  }
}

final appSettingsProvider = NotifierProvider<AppSettingsNotifier, AppSettings>(() {
  return AppSettingsNotifier();
});
