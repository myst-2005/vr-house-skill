// A / X = next room, B / Y = previous room (Quest controllers). Keyboard 1-9 in the editor.
using Unity.XR.CoreUtils;
using UnityEngine;
using UnityEngine.InputSystem;

public class RoomJumper : MonoBehaviour
{
    [System.Serializable]
    public struct Room { public string name; public float x, y, z, bearing; }

    public XROrigin origin;
    public Room[] rooms =
    {
        new Room { name = "Living", x = 9.2f, y = 13.1f, z = 0f, bearing = 225 },
        new Room { name = "Sit-out", x = 4.6f, y = 12.9f, z = -0.15f, bearing = 90 },
        new Room { name = "Dining", x = 6.3f, y = 8.1f, z = 0f, bearing = 135 },
        new Room { name = "Kitchen", x = 6.8f, y = 3.6f, z = 0f, bearing = 90 },
        new Room { name = "Home office", x = 4.7f, y = 10.3f, z = 0f, bearing = 270 },
        new Room { name = "Hall & pooja", x = 4.9f, y = 7.6f, z = 0f, bearing = 180 },
        new Room { name = "Mother's room", x = 3.1f, y = 3.3f, z = 0f, bearing = 270 },
        new Room { name = "Lobby (1st floor)", x = 4.3f, y = 8.2f, z = 3.15f, bearing = 180 },
        new Room { name = "Gaming room", x = 7.2f, y = 5.6f, z = 3.15f, bearing = 0 },
        new Room { name = "Master bedroom", x = 9.3f, y = 9.7f, z = 3.15f, bearing = 300 },
        new Room { name = "Children's room", x = 2.9f, y = 9.7f, z = 3.15f, bearing = 0 },
        new Room { name = "Terrace", x = 5.0f, y = 2.4f, z = 3.15f, bearing = 180 },
    };

    InputAction next, prev;
    int index;

    void OnEnable()
    {
        next = new InputAction("next", InputActionType.Button);
        next.AddBinding("<XRController>{RightHand}/primaryButton");
        next.AddBinding("<XRController>{LeftHand}/primaryButton");
        next.AddBinding("<Keyboard>/n");
        prev = new InputAction("prev", InputActionType.Button);
        prev.AddBinding("<XRController>{RightHand}/secondaryButton");
        prev.AddBinding("<XRController>{LeftHand}/secondaryButton");
        prev.AddBinding("<Keyboard>/p");
        next.performed += _ => Go(index + 1);
        prev.performed += _ => Go(index - 1);
        next.Enable(); prev.Enable();
    }

    void OnDisable() { next?.Disable(); prev?.Disable(); }

    void Start() { Go(0); }

    public void Go(int i)
    {
        if (origin == null || rooms.Length == 0) return;
        index = (i % rooms.Length + rooms.Length) % rooms.Length;
        var r = rooms[index];
        var feet = new Vector3(-r.x, r.z, -r.y);                       // plan -> Unity (same mapping as the model import)
        var cc = origin.GetComponent<CharacterController>();
        if (cc) cc.enabled = false;
        // face the room's bearing (0 = north = plan +y), then put the head over the spot
        float yaw = 180f + r.bearing;                                    // plan north (+y) is Unity -Z
        var cam = origin.Camera.transform;
        float camYaw = cam.eulerAngles.y;
        origin.transform.RotateAround(cam.position, Vector3.up, yaw - camYaw);
        var offset = new Vector3(cam.position.x - origin.transform.position.x, 0, cam.position.z - origin.transform.position.z);
        origin.transform.position = feet - offset;
        if (cc) cc.enabled = true;
    }
}
