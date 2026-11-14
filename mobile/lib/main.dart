import 'package:flutter/material.dart';

/// ARIA companion app entry point.
///
/// This is a UI-only scaffold: the microphone button and transcript area are
/// wired to local state so the screen is fully navigable without a backend.
/// Replace [_onMicPressed] with a real recorder + `/api/assistant/query` call.
void main() => runApp(const AriaApp());

class AriaApp extends StatelessWidget {
  const AriaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ARIA Assistant',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF5B6CFF)),
        useMaterial3: true,
      ),
      home: const AssistantScreen(),
    );
  }
}

class AssistantScreen extends StatefulWidget {
  const AssistantScreen({super.key});

  @override
  State<AssistantScreen> createState() => _AssistantScreenState();
}

class _AssistantScreenState extends State<AssistantScreen> {
  final List<String> _transcript = <String>[];
  bool _listening = false;

  void _onMicPressed() {
    setState(() {
      _listening = !_listening;
      if (_listening) {
        _transcript.add('Listening... (speak your command)');
      } else {
        _transcript.add('Processed locally — intent resolved.');
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ARIA Assistant')),
      body: Column(
        children: [
          Expanded(
            child: _transcript.isEmpty
                ? const Center(child: Text('Tap the microphone to start.'))
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _transcript.length,
                    itemBuilder: (context, index) =>
                        Card(child: ListTile(title: Text(_transcript[index]))),
                  ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  FloatingActionButton.large(
                    onPressed: _onMicPressed,
                    tooltip: 'Push to talk',
                    backgroundColor: _listening ? Colors.redAccent : null,
                    child: Icon(_listening ? Icons.mic : Icons.mic_none),
                  ),
                  const SizedBox(height: 8),
                  Text(_listening ? 'Listening (tap to stop)' : 'Offline-first • private'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
