
import { ChangeDetectionStrategy, Component } from "@angular/core";

const EXAMPLE_DOC = `{
    key: "ABC123",
    document: {
        alias:"A12345678COMP",
        name: "This is a circuit breaker ABC123",
        rating: "11kV"
    }
}`;

@Component({
    selector: "docdb-admin",
    templateUrl: "docdb-page.component.html",
    styleUrls: ["docdb-page.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DocdbPageComponent {
    protected readonly EXAMPLE_DOC = EXAMPLE_DOC;
}