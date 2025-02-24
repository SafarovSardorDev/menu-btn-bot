-- CreateEnum
CREATE TYPE "UserRole" AS ENUM ('owner', 'admin', 'user');

-- CreateEnum
CREATE TYPE "FormType" AS ENUM ('question', 'multiple_question', 'register', 'login');

-- CreateEnum
CREATE TYPE "FormFieldType" AS ENUM ('text', 'email', 'phone_number', 'photo', 'location', 'contact', 'full_name', 'first_name', 'last_name', 'language');

-- CreateEnum
CREATE TYPE "FormFieldAnswerType" AS ENUM ('message', 'inline_keyboard', 'keyboard');

-- CreateEnum
CREATE TYPE "MenuType" AS ENUM ('menu', 'live_chat', 'form');

-- CreateTable
CREATE TABLE "User" (
    "id" SERIAL NOT NULL,
    "telegramId" BIGINT NOT NULL,
    "firstName" TEXT,
    "lastName" TEXT,
    "isPremium" BOOLEAN,
    "isBot" BOOLEAN NOT NULL DEFAULT false,
    "languageCode" TEXT,
    "username" TEXT,
    "role" "UserRole" NOT NULL DEFAULT 'user',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3)
);

-- CreateTable
CREATE TABLE "Menu" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "parentId" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3)
);

-- CreateTable
CREATE TABLE "MenuMessage" (
    "id" SERIAL NOT NULL,
    "message" JSONB NOT NULL,
    "menuId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3)
);

-- CreateIndex
CREATE UNIQUE INDEX "User_id_key" ON "User"("id");

-- CreateIndex
CREATE UNIQUE INDEX "User_telegramId_key" ON "User"("telegramId");

-- CreateIndex
CREATE UNIQUE INDEX "Menu_id_key" ON "Menu"("id");

-- CreateIndex
CREATE UNIQUE INDEX "MenuMessage_id_key" ON "MenuMessage"("id");

-- AddForeignKey
ALTER TABLE "Menu" ADD CONSTRAINT "Menu_parentId_fkey" FOREIGN KEY ("parentId") REFERENCES "Menu"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "MenuMessage" ADD CONSTRAINT "MenuMessage_menuId_fkey" FOREIGN KEY ("menuId") REFERENCES "Menu"("id") ON DELETE CASCADE ON UPDATE CASCADE;
