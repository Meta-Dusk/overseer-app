import flet as ft
import time
from typing import TypeAlias, Optional, TypedDict, Callable

from utilities.dialogs.basic import WinMBIcon, WinMBButtons, WinMBResponse, WinMessageBox

DialogBranchDict: TypeAlias = dict[WinMBResponse, Optional[str]]
OptionalNarrationCallback: TypeAlias = Optional[Callable[[WinMBResponse], None]]

class NarrativeNode(TypedDict):
    title: str
    message: str
    buttons: WinMBButtons
    icon: WinMBIcon
    next: DialogBranchDict
    callback: OptionalNarrationCallback

NarrativeMap: TypeAlias = dict[str, NarrativeNode]

class NativeNarrator:
    """Manages branching conversations using Win32 dialog results."""
    def __init__(self, page: ft.Page) -> None:
        self.page = page

    def play_narrative(self, narrative_map: NarrativeMap, start_id: str = "start") -> None:
        """
        Traverses a branching narrative map.
        narrative_map: dict of { "id": { "message": str, "buttons": int, "next": DialogBranchDict } }
        """
        def _narrative_thread():
            current_id: Optional[str] = start_id
            
            while current_id and current_id in narrative_map:
                node = narrative_map[current_id]
                
                # Spawn and wait for result
                # MessageBoxW returns the ID of the button clicked
                mbox = WinMessageBox.spawn(
                    title=node.get("title", "The Overseer"),
                    message=node["message"],
                    icon=node.get("icon", WinMBIcon.INFO),
                    buttons=node.get("buttons", WinMBButtons.OK)
                )
                result: WinMBResponse = mbox()
                callback = node.get("callback")
                if callback: callback(result)
                
                # Determine the next node based on the button clicked
                next_map: DialogBranchDict = node.get("next", {})
                
                # If the result (i.e., 6 for YES) is in our 'next' map, go there
                # Otherwise, end the conversation (None)
                current_id = next_map.get(result)
                
                time.sleep(0.2)

        self.page.run_thread(_narrative_thread)
    
    def trigger_interrogation(self):
        def on_cancel_node(response: WinMBResponse) -> None:
            if response != WinMBResponse.CANCEL: return
            self.page.run_task(self.page.window.close)
        
        narrative: NarrativeMap = {
            "start": {
                "title": "Productivity Check",
                "message": (
                    "I see you've been doing nothing for a while now. "
                    "Did you finish your assessments?"
                ),
                "buttons": WinMBButtons.YESNO,
                "icon": WinMBIcon.QUESTION,
                "next": {
                    WinMBResponse.YES: "honesty",
                    WinMBResponse.NO: "denial"
                },
                "callback": None
            },
            "honesty": {
                "title": "The Overseer",
                "message": "Excellent. Self-awareness is the first step. Keep up the good work.",
                "buttons": WinMBButtons.OK,
                "icon": WinMBIcon.INFO,
                "next": { WinMBResponse.OK: None },
                "callback": None
            },
            "denial": {
                "title": "SECURITY BREACH",
                "message": "Lying is a violation of the productivity protocol. Prepare for system recalibration.",
                "buttons": WinMBButtons.OK,
                "icon": WinMBIcon.ERROR,
                "next": { WinMBResponse.OK: "glitch_trigger" },
                "callback": None
            },
            "glitch_trigger": {
                "title": "FATAL ERROR",
                "message": "0x0000DEAD: Internal Trust Corruption. Memory wipe initiated.",
                "buttons": WinMBButtons.RETRYCANCEL,
                "icon": WinMBIcon.ERROR,
                "next": {
                    WinMBResponse.RETRY: "denial",
                    WinMBResponse.CANCEL: None
                },
                "callback": on_cancel_node
            }
        }

        self.play_narrative(narrative)