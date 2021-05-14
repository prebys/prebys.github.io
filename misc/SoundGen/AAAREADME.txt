SoundGen waveform synthesiser. Can generate an arbitrary number of simultaneous audio waveforms with
different frequencies and other characteristics.

Runs on any machine that runs Java.  Tested on OSX, Windows 7, and Scientific Linux. 

Installing and running:
 - Download SoundGen.jar
 - If your machine has Java 1.6.0 or later, you can run straight from the JAR file, with
    > java -cp SoundGen.jar SoundGen
 - If your Java is older, or you want to edit the files.
    > jar xf SoundGen.jar        (this will unpack both the .class and .java files)
    (edit .java files as needed)
    > javac *.java
    > java SoundGen

Usage:

The first dialog box just has an "Add Waveform" button.  Click it to add one of three types of waveforms
   - Simple waveform:  Sine, Square, or Triangle, with a frequency and amplitude (0 to 32767)
   - Modulated waveform: Sinewave which is modulated in amplitude or frequency.  Specify the fundamental
     frequency and the amplitude and frequency of the modulation.
   - Damped waveform.  Since wave with an exponentially decaying amplitude and optionally a repeat time.

An arbitrary number of additional waveforms may be added. The will appear on a list, from which they can
be edited or deleted.  Total (sum) amplitude should never exceed 32767. This is not checked internally.
Might give unpredictable results if it happens.

Technical Details:
   - SoundGen.java: Main steering program.
   - WaveFormManager.java: does most of the work, by keeping track of the different WaveForm objects.
   - WaveForm.java: describes simple sine wave.
   - ModulatedWaveForm.java: extends WaveForm to a modulated wave.
   - DampedWaveForm.java:       "        "      " an exponentially decaying wave
   - AudioOutput.java: handles output to the sound card
   - AudioInput.java: handles input from sound card.  Not currently used.  Included for historical reasons.

=========================================

History:

   2000-2001  E.Prebys   Developed for Princeton University for Satellite Physics Freshman Seminar
   5-FEB-2016 E.Prebys   Cleaned up deprecated stuff to work with Java 1.8.  Compiled with Java 1.6.0 and released.


