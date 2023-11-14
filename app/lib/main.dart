import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'config.dart';
import 'resultPage.dart';

void main() => runApp(MaterialApp(
      home: Home(),
      debugShowCheckedModeBanner: false,
    ));

class Home extends StatefulWidget {
  @override
  _HomeState createState() => _HomeState();
}

class _HomeState extends State<Home> {
  XFile? image;

  String serverResponse = '';

  final ImagePicker picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance!.addPostFrameCallback((_) => showWarningDialog());
  }

  Future<void> uploadImage(File imageFile) async {
    var url = 'http://192.168.31.47:50000/images'; // Use Own URL
    // var url = serverUrl;

    var request = http.MultipartRequest('POST', Uri.parse(url));
    request.files
        .add(await http.MultipartFile.fromPath('file', imageFile.path));

    var response = await request.send();
    var responseBody = await response.stream.bytesToString();

    // Convert the response body to a JSON object
    var jsonData = jsonDecode(responseBody);

    if (jsonData.containsKey('predicted_class')) {
      var predictedLabel = jsonData['predicted_class'];
      var edible = jsonData['edible'];
      var reference = jsonData['reference'];
      var note = jsonData['note'];

      setState(() {
        this.serverResponse =
            predictedLabel; // Update the serverResponse variable
      });

      Future.delayed(Duration(seconds: 1), () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ResultPage(
              imagePath: image!.path,
              predictedLabel: predictedLabel,
              edible: edible,
              reference: reference,
              note: note,
            ),
          ),
        );
      });
    }
  }

  //we can upload image from camera or from gallery based on parameter
  Future getImage(ImageSource media) async {
    var img = await picker.pickImage(source: media);

    setState(() {
      image = img;
    });

    if (image != null) {
      File imageFile = File(image!.path);
      await uploadImage(imageFile);
    }
  }

  //show popup dialog
  void myAlert() {
    showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            title: Text('Please choose media to select'),
            content: Container(
              height: MediaQuery.of(context).size.height / 6,
              child: Column(
                children: [
                  ElevatedButton(
                    //if user click this button, user can upload image from gallery
                    onPressed: () {
                      Navigator.pop(context);
                      getImage(ImageSource.gallery);
                    },
                    child: Row(
                      children: [
                        Icon(Icons.image),
                        Text('From Gallery'),
                      ],
                    ),
                  ),
                  ElevatedButton(
                    //if user click this button. user can upload image from camera
                    onPressed: () {
                      Navigator.pop(context);
                      getImage(ImageSource.camera);
                    },
                    child: Row(
                      children: [
                        Icon(Icons.camera),
                        Text('From Camera'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        });
  }

  void showWarningDialog() {
    showDialog(
        context: context,
        barrierDismissible: false, // User must tap button to close dialog!
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text('IMPORTANT WARNING'),
            content: Text(
                'The classifications provided by this application are for educational purposes only and should NOT be used as a substitute for professional advice or guidance. Please consult with a trained mycologist, field guide, or other reliable resources before consuming any wild mushrooms. Incorrect identification can lead to serious health issues or even death. Use this application at your own risk.'),
            actions: [
              ElevatedButton(
                child: Text('I Understand'),
                onPressed: () {
                  Navigator.of(context).pop(); // Close the dialog
                },
              ),
            ],
          );
        });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('MushroomSafe'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: () {
                myAlert();
              },
              child: Text('Upload Photo'),
            ),
          ],
        ),
      ),
    );
  }
}
