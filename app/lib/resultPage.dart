import 'dart:io';

import 'package:flutter/material.dart';

class ResultPage extends StatelessWidget {
  final String imagePath;
  final String predictedLabel;
  final String edible;
  final String reference;
  final String note;

  ResultPage({
    required this.imagePath,
    required this.predictedLabel,
    required this.edible,
    required this.reference,
    required this.note,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Result'),
      ),
      body: Column(
        // mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(height: 10),
          Image.file(
            File(imagePath),
            width: MediaQuery.of(context).size.width,
            height: 300,
          ),
          SizedBox(height: 10),
          Text(
            'Predicted Class: $predictedLabel',
            style: TextStyle(fontSize: 16),
          ),
          SizedBox(height: 10),
          Row(
            children: [
              Icon(
                edible == 'e' ? Icons.check_circle : Icons.warning,
                color: edible == 'e' ? Colors.green : Colors.red,
              ),
              SizedBox(width: 5),
              Text(
                edible == 'e' ? 'Edible' : 'Inedible',
                style: TextStyle(fontSize: 16),
              ),
            ],
          ),
          SizedBox(height: 10),
          Text(
            'Note: $note',
            style: TextStyle(fontSize: 16),
          ),
          SizedBox(height: 10),
          Text(
            'Reference: $reference',
            style: TextStyle(fontSize: 16),
          ),
        ],
      ),
    );
  }
}
