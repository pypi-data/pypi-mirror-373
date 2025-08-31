import { AppWebPage } from "./app.po";

describe("build-web App", () => {
  let page: AppWebPage;

  beforeEach(() => {
    page = new AppWebPage();
  });

  it("should display message saying app works", () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual("app works!");
  });
});
