import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:{KAVIA_TEMPLATE_PROJECT_NAME}/main.dart';

void main() {
  testWidgets('App generation message displayed', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('{KAVIA_TEMPLATE_PROJECT_NAME} App is being generated...'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('App bar has correct title', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('{KAVIA_TEMPLATE_PROJECT_NAME}'), findsOneWidget);
  });
}
