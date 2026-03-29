import { GalleryVerticalEnd } from "lucide-react";
import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <div className="bg-muted flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="flex w-full max-w-sm flex-col gap-6">
        <a href="/" className="flex flex-col items-center gap-2 self-center font-medium">
          <div className="bg-primary text-primary-foreground flex size-12 items-center justify-center rounded-md text-2xl">
            💹
          </div>
          <span className="text-2xl font-bold">FinSight</span>
          <span className="text-sm text-muted-foreground">Your finances, intelligently managed.</span>
        </a>
        <LoginForm />
      </div>
    </div>
  );
}
