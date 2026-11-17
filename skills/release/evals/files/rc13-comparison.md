# v2.2.2-rc.12 → v2.2.2-rc.13

## UI and test excerpts from the release interval

Commit title: `style(moment-timeline): reduce creation complexity`

```diff
-<button>Create Timeline</button>
+<button [disabled]="activities.length < 2">Create Timeline</button>

-@if (canAttend) {
+@if (canAttend && activities.some(a => !joinedIds.includes(a.id))) {
   <button>Join the whole program</button>
 }

-saveMoment(await chooseWhetherToNotify());
+const choice = await confirmDateChange({
+  notify: localStorage.getItem("notifyMomentDateChange") !== "false",
+});
+if (choice.dismissed) return;
+localStorage.setItem("notifyMomentDateChange", String(choice.notify));
+saveMoment(choice.notify);
```

```js
it("keeps the draft when the confirmation is dismissed", async () => {
  await dismissDateConfirmation();
  expect(updateMoment).not.toHaveBeenCalled();
  expect(notifyDateChange).not.toHaveBeenCalled();
  expect(page.isEditing()).toBe(true);
});
```
