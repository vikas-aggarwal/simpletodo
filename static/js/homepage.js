import { Controller, Application } from "./stimulus.js"

class OverlayController extends Controller {
    hideModal(event) {
        this.element.parentElement.removeAttribute("src");
        this.element.remove();
    }

    hideModalFromFrame(event) {
        if(event.target.id == "overlay") {
            this.hideModal(event)
        }
    }
}



window.Stimulus = Application.start()
Stimulus.register("overlay", OverlayController)



addEventListener("turbo:before-frame-render", (event) => {
    document.getElementById("overlay").style.display = "block";
  })

addEventListener("turbo:submit-end", (event) => {
    console.log(event.detail)
    if(event.detail.success) {
        
    }
})
