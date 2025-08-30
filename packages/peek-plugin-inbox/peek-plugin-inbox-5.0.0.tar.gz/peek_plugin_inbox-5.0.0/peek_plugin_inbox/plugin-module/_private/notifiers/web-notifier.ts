import { ISound, Sound } from "@synerty/peek-plugin-base-js";
import { NotifierI } from "./notifier.interface";

export class WebNotifier implements NotifierI {
    private alertSound: ISound;

    loadSound(soundFilePath: string) {
        try {
            this.alertSound = new Sound(soundFilePath);
        } catch (e) {
            console.log(`Failed to load sound: ${e}`);
            this.alertSound = null;
        }
    }
    playSound() {
        try {
            const optionalPromise = this.alertSound && this.alertSound.play();
            if (optionalPromise != null) {
                optionalPromise.catch((err) => {
                    console.log(`Failed to play alert sound\n${err}`);
                });
            }
        } catch (e) {
            console.log(`Error playing sound: ${e.toString()}`);
        }
    }
}
