"use strict";

class KeybordNav {
    constructor() {

        this.taskList = document.querySelectorAll(".taskList");
        this.selectedTaskInList = -1;
        this.init()
        this.mode = "HOME"; //other options MANAGE, FILTER



        //MANAGE MODE
        this.selectedOccurence = -1;

        window.addEventListener("turbo:load", () => {
            this.taskList = document.querySelectorAll(".taskList");
            this.mode = "HOME"
            this.init();
        });

        window.addEventListener("turbo:frame-render", (event) => {
            if (event.detail.fetchResponse.location.pathname.indexOf("todos/manage") != -1) {
                this.mode = "MANAGE";
                this.initManage();
            }
            else {
                this.mode = "HOME";
            }

        });



        document.addEventListener("keydown", (event) => {

            if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
                // If it is, return early and ignore the event for the document listener
                return;
            }

            if (this.mode == "HOME") {
                switch (event.key) {
                    case "ArrowLeft":
                        this.moveLeft();
                        break;
                    case "ArrowUp":
                        this.moveUp();
                        break;
                    case "ArrowRight":
                        this.moveRight();
                        break;
                    case "ArrowDown":
                        this.moveDown();
                        break;
                    case "d":
                        this.markAsDone()
                        break;
                    case "r":
                        this.resetMark()
                        break;
                    case "s":
                        this.markAsSkip()
                        break;
                    case "f":
                        this.invokeFilter()
                        break;
                    case "m":
                        this.invokeManage()
                        break;
                    default:
                        return; // Exit for other keys
                }
            }
            else if(this.mode == "MANAGE") {
                 switch (event.key) {
                    case "ArrowUp":
                        this.moveUpOccurrence();
                        break;
                    case "ArrowDown":
                        this.moveDownOccurrence();
                        break;
                    case "d":
                        this.markAsDoneOccurrence()
                        break;
                    case "s":
                        this.markAsSkipOccurrence()
                        break;
                    case "Enter":
                        this.submitManageForm()
                        break;
            }
        }
            event.preventDefault(); // Prevent default action (e.g., page scrolling)
        });
    }

    initManage() {
        let manageHabitForm = document.getElementsByName("manageHabitTaskForm")[0];
        if (manageHabitForm.querySelectorAll(".occurrence").length > 0) {
            this.selectedOccurence = 0;
            this.highlightSeletedOccurrence();
        }
    }

    submitManageForm() {
        document.getElementsByName("manageHabitTaskForm")[0].submit();
    }

    moveDownOccurrence() {
        let manageHabitForm = document.getElementsByName("manageHabitTaskForm")[0];
        if (this.selectedOccurence != -1 && manageHabitForm.querySelectorAll(".occurrence").length > this.selectedOccurence + 1 ) {
            this.unHighlightSeletedOccurrence()
            this.selectedOccurence++;
            this.highlightSeletedOccurrence();
        }
    }

    moveUpOccurrence() {
        let manageHabitForm = document.getElementsByName("manageHabitTaskForm")[0];
        if (this.selectedOccurence != -1 && manageHabitForm.querySelectorAll(".occurrence").length > this.selectedOccurence - 1 ) {
            this.unHighlightSeletedOccurrence()
            this.selectedOccurence--;
            this.highlightSeletedOccurrence();
        }
    }

    highlightSeletedOccurrence() {
        if (this.selectedOccurence != -1) {
            document.getElementsByName("manageHabitTaskForm")[0].querySelectorAll(".occurrence")[this.selectedOccurence].classList.add("selected");
        }
    }

    unHighlightSeletedOccurrence() {
        if (this.selectedOccurence != -1) {
            document.getElementsByName("manageHabitTaskForm")[0].querySelectorAll(".occurrence")[this.selectedOccurence].classList.remove("selected");
        }
    }

    markAsDoneOccurrence() {
        document.getElementsByName("manageHabitTaskForm")[0].querySelectorAll(".occurrence")[this.selectedOccurence].querySelectorAll('input[value="Done"]')[0].checked = true
    }

    markAsSkipOccurrence() {
        document.getElementsByName("manageHabitTaskForm")[0].querySelectorAll(".occurrence")[this.selectedOccurence].querySelectorAll('input[value="Skip"]')[0].checked = true
    }



    init() {

        let currentTaskList = 0;
        while (this.taskList.length > currentTaskList) {
            this.selectedTaskList = currentTaskList

            if (this.selectedTaskList >= 0) {
                let tasks = this.taskList[this.selectedTaskList].querySelectorAll(".task")
                if (tasks.length > 0) {
                    this.selectedTaskInList = 0
                    this.highlightSeletedTask(this.selectedTaskList, this.selectedTaskInList)
                    break;
                }

            }
            currentTaskList++;
        }



    }

    invokeManage() {
        Turbo.visit(document.querySelectorAll(".taskList")[this.selectedTaskList].querySelectorAll(".task")[this.selectedTaskInList].querySelectorAll('.manage-button')[0].href, { frame: "overlay" })
    }
    invokeFilter() {
        Turbo.visit(document.getElementById("new_filter").href, { frame: "overlay" })
    }

    markAsDone() {
        document.querySelectorAll(".taskList")[this.selectedTaskList].querySelectorAll(".task")[this.selectedTaskInList].querySelectorAll('input[value="Done"]')[0].checked = true
    }

    resetMark() {
        document.querySelectorAll(".taskList")[this.selectedTaskList].querySelectorAll(".task")[this.selectedTaskInList].querySelectorAll('input[value="None"]')[0].checked = true
    }

    markAsSkip() {
        document.querySelectorAll(".taskList")[this.selectedTaskList].querySelectorAll(".task")[this.selectedTaskInList].querySelectorAll('input[value="Skip"]')[0].checked = true
    }

    isTaskSelected() {
        return this.selectedTaskList != -1 && this.selectedTaskInList != -1
    }

    moveRight() {
        if (this.isTaskSelected()) {
            let currentSelectedTaskList = this.selectedTaskList;
            while (this.taskList.length > currentSelectedTaskList + 1) {
                if (this.taskList[currentSelectedTaskList + 1].querySelectorAll(".task").length > 0) {
                    this.unHighlightSeletedTask(this.selectedTaskList, this.selectedTaskInList);
                    this.selectedTaskInList = 0
                    this.selectedTaskList = currentSelectedTaskList + 1
                    this.highlightSeletedTask(this.selectedTaskList, this.selectedTaskInList);
                    break;
                }
                currentSelectedTaskList++;
            }
        }
    }


    moveLeft() {
        if (this.isTaskSelected()) {
            let currentSelectedTaskList = this.selectedTaskList;
            while (this.taskList.length > 0 && currentSelectedTaskList - 1 >= 0) {
                if (this.taskList[currentSelectedTaskList - 1].querySelectorAll(".task").length > 0) {
                    this.unHighlightSeletedTask(this.selectedTaskList, this.selectedTaskInList);
                    this.selectedTaskList = currentSelectedTaskList - 1;
                    this.selectedTaskInList = 0
                    this.highlightSeletedTask(this.selectedTaskList, this.selectedTaskInList);
                    break;
                }
                currentSelectedTaskList--;
            }
        }
    }

    moveDown() {
        if (this.isTaskSelected()) {

            if (this.taskList[this.selectedTaskList].querySelectorAll(".task").length > this.selectedTaskInList + 1) {
                this.unHighlightSeletedTask(this.selectedTaskList, this.selectedTaskInList);
                this.selectedTaskInList++
                this.highlightSeletedTask(this.selectedTaskList, this.selectedTaskInList);
            }

        }
    }

    moveUp() {
        if (this.isTaskSelected()) {

            if (this.taskList[this.selectedTaskList].querySelectorAll(".task").length > 0 && this.selectedTaskInList - 1 >= 0) {
                this.unHighlightSeletedTask(this.selectedTaskList, this.selectedTaskInList);
                this.selectedTaskInList--;
                this.highlightSeletedTask(this.selectedTaskList, this.selectedTaskInList);
            }

        }
    }


    highlightSeletedTask(list, taskInList) {
        document.querySelectorAll(".taskList")[list].querySelectorAll(".task")[taskInList].classList.add("selected")
    }

    unHighlightSeletedTask(list, taskInList) {
        document.querySelectorAll(".taskList")[list].querySelectorAll(".task")[taskInList].classList.remove("selected")
        document.querySelectorAll(".taskList")[list].querySelectorAll(".task")[taskInList].scrollIntoView({ block: "center" })
    }

}

var keyb = new KeybordNav()